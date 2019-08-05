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


More detailed installation instructions can be found in the `SIRIUS readme`_.

.. _Sirius Readme: https://github.com/electronic-structure/SIRIUS/tree/develop


SIRIUS input file
=================

.. code-block:: json

  {
      "control" : {
          "processing_unit" : "cpu",
          "std_evp_solver_type" : "lapack",
          "gen_evp_solver_type" : "lapack",
          "verbosity" : 0
      },

      "parameters" : {
          "electronic_structure_method" : "pseudopotential",
          "xc_functionals" : ["XC_GGA_X_PBE", "XC_GGA_C_PBE"],
          "smearing_width" : 0.00025,
          "num_mag_dims" : 0,
          "gk_cutoff" : 7,
          "pw_cutoff" : 25.00,
          "use_symmetry": false,
          "ngridk" : [1, 1, 1],
          "num_dft_iter": 30,
          "potential_tol": 1e-8,
          "energy_tol": 1e-8,
          "gamma_point": true
      },
      "iterative_solver" : {
          "type" : "davidson",
          "converge_by_energy" : 1
      },
      "unit_cell" : {
          "lattice_vectors" : [ [1.0, 0.0, 0.0],
                                [0.0, 1.0, 0.0],
                                [0.0, 0.0, 1.0]
                              ],
          "lattice_vectors_scale": 10,
          "atom_coordinate_units": "au",
          "atom_types" : ["H", "O"],
          "atom_files" : {
              "H"  : "H.json",
              "O"  : "O.json"
          },
          "atoms" : {
              "H": [
                  [2.000, 0.000, 0.000],
                  [0.000, 0.000, 0.000]
              ],
              "O": [
                  [1.000, 0.000, 0.000]
              ]
          }
      },
      "mixer" : {
          "beta" : 0.8
      }

  }
