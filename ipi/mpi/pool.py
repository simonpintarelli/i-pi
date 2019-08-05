from mpi4py import MPI
import dill
# need to use this as a workaorund to pickle functions
MPI.pickle.__init__(dill.dumps, dill.loads)

__all__ = ['Executor']


class Executor:
    def __init__(self, ngroups=1):
        """
        """
        if 0 < MPI.COMM_WORLD.rank < (MPI.COMM_WORLD.size - (
            (MPI.COMM_WORLD.size - 1) % ngroups)):
            MPI.COMM_GROUP = MPI.COMM_WORLD.Split(
                (MPI.COMM_WORLD.rank - 1) % ngroups,
                (MPI.COMM_WORLD.rank - 1) // ngroups)
            MPI.COMM_GROUP.name = "comm_group_{}".format(
                (MPI.COMM_WORLD.rank - 1) % ngroups)
        else:
            MPI.COMM_GROUP = MPI.COMM_WORLD.Split(MPI.UNDEFINED,
                                                  MPI.COMM_WORLD.rank)

        if MPI.COMM_WORLD.rank == 0 or (MPI.COMM_GROUP
                                        and MPI.COMM_GROUP.rank == 0):
            MPI.COMM_JOB = MPI.COMM_WORLD.Split(0, MPI.COMM_WORLD.rank)
        else:
            MPI.COMM_JOB = MPI.COMM_WORLD.Split(MPI.UNDEFINED,
                                                MPI.COMM_WORLD.rank)

        self._MPI = MPI

    def __exit__(self, exc_type, exc_value, traceback):

        if MPI.COMM_WORLD.rank == 0:
            # send exit message to job roots
            for i in range(1, MPI.COMM_JOB.size):
                self.submit(None, dest=i)

    def _jobs_loop(self):

        while True:
            work_future = MPI.COMM_JOB.irecv(source=0)
            work = work_future.wait()
            MPI.COMM_GROUP.bcast(work, root=0)
            if work is None:
                return
            func = work['func']
            payload = work['payload']
            # add MPI communicator
            payload['mpicomm'] = MPI.COMM_GROUP
            result = func(payload)
            # return the result to master rank
            MPI.COMM_JOB.isend(result, dest=0)

    def _workers_loop(self):

        while True:
            work = MPI.COMM_GROUP.bcast(None, root=0)
            if work is None:
                return
            func = work['func']
            payload = work['payload']
            # add MPI communicator
            payload['mpicomm'] = MPI.COMM_GROUP
            func(payload)

    def submit(self, work, dest):
        """
        Submits a job (async) and returns an MPI request object which can
        be queried for the result.

        Keyword Arguments:
        work -- a dictionary which must contain keys 'func', and 'payload'
                workers then call func(payload)
        dest -- destination rank in MPI.COMM_JOB communicator
        """

        assert dest > 0 and dest < MPI.COMM_JOB.size

        MPI.COMM_JOB.isend(work, dest=dest)
        if work is None:
            return

        req = MPI.COMM_JOB.irecv(None, source=dest)
        return req

    def __enter__(self):

        if MPI.COMM_JOB != MPI.COMM_NULL and MPI.COMM_WORLD.rank != 0:
            self._jobs_loop()
            # done with loop, now exit
            return
        elif MPI.COMM_GROUP != MPI.COMM_NULL and MPI.COMM_WORLD.rank != 0:
            self._workers_loop()
            # done with loop, now exit
            return
        if MPI.COMM_JOB == MPI.COMM_NULL and MPI.COMM_GROUP == MPI.COMM_NULL:
            # this rank is not part of the executor
            return
        else:
            return self


if __name__ == '__main__':
    def fun(work):
        myrank = MPI.COMM_WORLD.rank
        print('from rank %d' % myrank, 'got: ', work)
        return True

    with Executor(ngroups=2) as executor:
        if executor is not None:
            work = {'func': fun, 'payload': 'work chunk'}
            res1 = executor.submit(work, dest=1)
            work = {'func': fun, 'payload': 'second chunk'}
            res2 = executor.submit(work, dest=2)
            work = {'func': fun, 'payload': 'last chunk'}
            res3 = executor.submit(work, dest=1)
            res1.wait()
            res2.wait()
            res3.wait()

    MPI.COMM_WORLD.Barrier()
