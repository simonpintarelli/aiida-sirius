# -*- coding: utf-8 -*-
"""Submit a test calculation on localhost.

Usage: verdi run submit.py
"""

from __future__ import absolute_import
from __future__ import print_function
import os
from aiida_sirius import tests, helpers
from aiida.plugins import DataFactory, CalculationFactory
from aiida.engine import run
from aiida.orm.nodes.data.upf import get_pseudos_from_structure
import json

# get code
computer = helpers.get_computer('localhost')
code = helpers.get_code(entry_point='sirius.py.nlcg', computer=computer)

params = {
        "electronic_structure_method": "pseudopotential",
        "xc_functionals": ["XC_GGA_X_PBE", "XC_GGA_C_PBE"],
        "smearing_width": 0.025,
        "use_symmetry": True,
        "num_mag_dims": 1,
        "gk_cutoff": 6.0,
        "pw_cutoff": 27.00,
        "num_dft_iter": 2
}
# Prepare input parameters
SiriusParameters = DataFactory('sirius.scf')
StructureData = DataFactory('structure')
KpointsData = DataFactory('array.kpoints')
parameters = SiriusParameters({'control': {},
                               'iterative_solver': {},
                               'parameters': params,
                               'mixer': {}})
SinglefileData = DataFactory('singlefile')

NLCGParameters = DataFactory('sirius.py.nlcg')
nlcg_marzari = {'type': 'Marzari', 'inner': 2, 'fd_slope_check': False}
precond = {'type': 'kinetic', 'eps': 0.001}
nlcgconfig = {
    "CG": {
        "method": nlcg_marzari,
        "type": "FR",
        "maxiter": 5,
        "restart": 20,
        "tau": 0.1,
        "nscf": 1,
        "precond": precond,
        "tol": 1e-09,
    },
    "System": {"T": 300.0, "smearing": "gaussian-spline"},
}
nlcgparams = NLCGParameters(nlcgconfig)


alat = 4. # angstrom
cell = [[alat, 0., 0.,],
        [0., alat, 0.,],
        [0., 0., alat,],
       ]
s = StructureData(cell=cell)
s.append_atom(position=(0.,0.,0.),symbols='Ba')
s.append_atom(position=(alat/2.,alat/2.,alat/2.),symbols='Ti')
s.append_atom(position=(alat/2.,alat/2.,0.),symbols='O')
s.append_atom(position=(alat/2.,0.,alat/2.),symbols='O')
s.append_atom(position=(0.,alat/2.,alat/2.),symbols='O')

kpoints = KpointsData()
kpoints.set_kpoints_mesh([2, 2, 2])

comp_resources = {'num_mpiprocs_per_machine': 2,
                  'num_machines': 1,
                  'num_cores_per_mpiproc': 1}

# set up calculation
inputs = {
    'code': code,
    'sirius_config': parameters,
    'structure': s,
    'kpoints': kpoints,
    'nlcgparams': nlcgparams,
    'metadata': {
        'description': "Test job submission with the aiida_sirius plugin",
        'options': {
            'resources': comp_resources,
            'max_wallclock_seconds': 100,
            'withmpi': True
        }
    },
    'pseudos': get_pseudos_from_structure(s, 'normcons')
}

# Note: in order to submit your calculation to the aiida daemon, do:
# from aiida.engine import submit
# future = submit(CalculationFactory('sirius'), **inputs)
calc = CalculationFactory('sirius.py.nlcg')
result = run(calc, **inputs)
