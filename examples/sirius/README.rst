Installing SIRIUS
=================

Instructions can be found in the `SIRIUS readme`_.

.. _Sirius Readme: https://github.com/electronic-structure/SIRIUS/tree/develop


Running i-PI + SIRIUS
=====================

SIRIUS provides Python bindings which allows to run it directly within i-PI,
making the socket interface obsolete.

.. code-block:: bash

   OMP_NUM_THREADS=1 mpirun -np 5 i-pi -n4 input.xml

The above command will start 5 MPI ranks. One is always dedicated to the i-PI
control server, the remaining ones will be distributed to the MPI worker pools
running the SIRIUS instances. For example ``mpirun -np 21 i-pi -n 5`` would create
``5`` worker pools each consisting of ``4`` ranks.

i-PI `input.xml`
===============

Please take one of the files in ``examples/sirius`` as a template.

SIRIUS ``sirius.json`` input file
=================================

SIRIUS reads from the `sirius.json` input file which must reside in work
directory. It is structured into the `control`, `parameters`,
`iterative_solver`, `unit_cell` and `mixer` section.

control
-------

.. code-block:: json

   "control": {
      "processing_unit": "gpu",
      "verbosity": 0
   }

The ``procssing_unit`` is either ``cpu`` or ``gpu``. ``verbosity`` is either ``0``, ``1`` or
``2`` (debug output).

parameters
----------

.. code-block:: json

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
   }

The ``xc_functionals`` are ``["XC_GGA_X_PBE", "XC_GGA_C_PBE"]`` for GGA or
``["XC_LDA_X", "XC_LDA_C_PZ"]`` for Perdew-Zunger LDA. A full list of available
functionals can be found in the `SIRIUS github repository`_ in the file
`xc functionals base`_ .

``num_mag_dims`` can be either ``0`` (non-magnetic), ``1`` or ``3``.

Further parameters are:

- ``gk_cutoff``: wave-function cutoff
- ``pw_cutoff``: plane-wave cutoff (density)
- ``num_dft_iter``: maximal number of SCF iterations
- ``ngridk``: k-point grid

Unit cell
---------


.. code-block:: json

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
   }

Contains the structure and the names of the pseudo-potential input files
(``atom_files``). If ``atom_coordinate_units`` is unspecified the atom coordinates
are given relative to the unit cell. ``atom_coordinate_units`` can also be ``au``
(atomic units) or ``A`` for Ångstrom.

The ``lattice_vectors`` are scaled by the factor ``lattice_vectors_scale`` (default
=1). The units are always in atomic units (independent of what is used for
``atomic_coordinate_units``).

The full ``sirius.json`` file then looks like the following:

.. code-block:: json

  {
      "control" : {
          "mpi_grid_dims": [1,1],
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



Conversion from UPF to JSON
===========================

SIRIUS provides a python script to convert UPF files to JSON format

Usage: (will create the file ``Ga.json``)

.. code-block:: bash

     wget http://www.pseudo-dojo.org/pseudos/nc-sr-04_pbe_standard/Ga.upf.gz?download
     upf_to_json G*upf

The `upf_to_json` executable can be found in the `SIRIUS github repository`_ in
the directory ``apps/upf`` and will be installed to `CMAKE_INSTALL_PREFIX/bin`.


.. _xc functionals base: https://github.com/electronic-structure/SIRIUS/blob/master/src/Potential/xc_functional_base.hpp
.. _SIRIUS github repository: https://github.com/electronic-structure/SIRIUS
