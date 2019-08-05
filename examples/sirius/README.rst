Installing SIRIUS
=================

Assuming the minimal dependencies FFTW, BLAS, Spglib, Libxc, GSL are installed in standard system paths,
run the following commands to build and install SIRIUS with CUDA and support for Python 2.7:

.. code:: bash

          git clone https://github.com/electronic-structure/SIRIUS.git -b develop
          mkdir -p SIRIUS/build
          cd SIRIUS/build
          cmake -DCMAKE_INSTALL_PREFIX=$HOME/local/sirius \
            -DCREATE_PYTHON_MODULE=On \
            -DUSE_CUDA=On \
            -DUSE_ELPA=Off \
            -DUSE_MKL=Off \
            -DUSE_MAGMA=Off \
            -DPYTHON2=On \
            ../
          make install

If the dependencies are not located in system directories, the following environment variables can be set to point cmake to the right place:

- FFTWROOT
- LIBSPGROOT
- LIBXCROOT
- HDF5_ROOT
- GSL_ROOT_DIR
- MAGMAROOT (optional, default OFF)
- MKLROOT (optional, default OFF)
- ELPAROOT (optional, default oFF)


The `PYTHONPATH` must be set accordingly, e.g for the CMAKE_INSTALL_PREFIX specified above:

.. code:: bash

   export PYTHONPATH=${HOME}/local/sirius/lib/python2.7/site-packages


More detailed installation instructions can be found in the `Sirius readme`_.

.. _Sirius Readme: https://github.com/electronic-structure/SIRIUS/tree/develop
