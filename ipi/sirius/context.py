import functools
import threading
import json
import sirius
import numpy as np
import time

lock = threading.Lock()

__all__ = ['SiriusCTX']


def periodic_dist(a, b):
    d = np.abs(b-a)
    dp = np.fmin(d, 1-d)
    return np.linalg.norm(dp, ord='fro')

def synchronized(lock):
    """ Synchronization decorator """
    def wrapper(f):
        @functools.wraps(f)
        def inner_wrapper(*args, **kw):
            with lock:
                return f(*args, **kw)

        return inner_wrapper

    return wrapper


class Singleton(type):
    _instances = {}

    @synchronized(lock)
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(
                *args, **kwargs)
        return cls._instances[cls]


class SiriusCTX:
    __metaclass__ = Singleton

    def __init__(self, mpicomm, input_file='sirius.json'):
        siriusJson = json.load(open(input_file, 'r'))
        self.sirius_comm = sirius_comm = sirius.make_sirius_comm(mpicomm)
        self.mpicomm = mpicomm
        self.ctx = sirius.Simulation_context(json.dumps(siriusJson),
                                             sirius_comm)
        self.ctx.initialize()

        if "shiftk" in siriusJson["parameters"]:
            shiftk = siriusJson["parameters"]["shiftk"]
        else:
            shiftk = [0, 0, 0]

        if "ngridk" in siriusJson["parameters"]:
            ngridk = siriusJson["parameters"]["ngridk"]
        else:
            ngridk = [1, 1, 1]

        if "num_dft_iter" in siriusJson["parameters"]:
            self.num_dft_iter = siriusJson["parameters"]["num_dft_iter"]
        else:
            self.num_dft_iter = 100

        if "potential_tol" in siriusJson["parameters"]:
            self.potential_tol = siriusJson["parameters"]["potential_tol"]
        else:
            self.potential_tol = 1e-5

        if "energy_tol" in siriusJson["parameters"]:
            self.energy_tol = siriusJson["parameters"]["energy_tol"]
        else:
            self.energy_tol = 1e-5

        use_symmetry = False
        self.kset = sirius.K_point_set(self.ctx, ngridk, shiftk, use_symmetry)
        self.dft_gs = sirius.DFT_ground_state(self.kset)
        self.dft_gs.initial_state()

    def _evaluate(self, r):
        ctx = self.ctx
        ih = r["cell"][1]
        cell = r["cell"][0]
        pos = r["pos"].reshape(-1, 3)
        rpos = np.mod(np.dot(ih, pos.T).T, 1)
        natoms = rpos.shape[0]

        prev_rpos = sirius.atom_positions(ctx.unit_cell())
        dx2 = periodic_dist(rpos, prev_rpos)
        sirius.set_atom_positions(ctx.unit_cell(), rpos)
        previous_cell = np.array(self.ctx.unit_cell().lattice_vectors())
        self.ctx.unit_cell().set_lattice_vectors(*cell)
        self.dft_gs.update()

        cell_volume = np.linalg.det(cell)
        pcell_volume = np.linalg.det(previous_cell)

        if dx2 / natoms > 1e-2 or r['sirius_restart']:
            self.dft_gs.initial_state()
        # reset wavefunctions
        sirius.initialize_subspace(self.dft_gs, self.ctx)

        rjson = self.dft_gs.find(
            potential_tol=self.potential_tol,
            energy_tol=self.energy_tol,
            initial_tol=1e-2,
            num_dft_iter=self.num_dft_iter,
            write_state=False)
        if not rjson["converged"]:
            print('SIRIUS failed to converge!')
            assert False

        forces = np.array(self.dft_gs.forces().calc_forces_total()).T
        assert forces.shape[1] == 3
        v = self.dft_gs.total_energy()

        stress = np.array(self.dft_gs.stress().calc_stress_total())
        vir = -1 * stress * cell_volume
        r["result"] = [v, forces.reshape(-1), vir, ""]
        r["status"] = "Done"
        r["t_finished"] = time.time()

        return r

    @staticmethod
    def run(r):
        mpicomm = r['mpicomm']
        if 'sirius_config' in r:
            sirius_config = r['sirius_config']
        else:
            sirius_config = 'sirius.json'
        obj = SiriusCTX(mpicomm, sirius_config)
        return obj._evaluate(r)
