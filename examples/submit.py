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
computer = helpers.get_computer()
code = helpers.get_code(entry_point='sirius.scf', computer=computer)

params = {
        "electronic_structure_method": "pseudopotential",
        "xc_functionals": ["XC_GGA_X_PBE", "XC_GGA_C_PBE"],
        "smearing_width": 0.025,
        "use_symmetry": True,
        "num_mag_dims": 1,
        "gk_cutoff": 6.0,
        "pw_cutoff": 27.00,
        "num_dft_iter": 100,
        "ngridk": [1, 1, 1],
}
# Prepare input parameters
SiriusParameters = DataFactory('sirius.scf')
StructureData = DataFactory('structure')
parameters = SiriusParameters({'control': {},
                               'iterative_solver': {},
                               'parameters': params,
                               'mixer': {}})
SinglefileData = DataFactory('singlefile')


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

# set up calculation
inputs = {
    'code': code,
    'sirius_config': parameters,
    'structure': s,
    'metadata': {
        'description': "Test job submission with the aiida_sirius plugin",
    },
    'pseudos': get_pseudos_from_structure(s, 'sssp_efficiency')
}

# Note: in order to submit your calculation to the aiida daemon, do:
# from aiida.engine import submit
# future = submit(CalculationFactory('sirius'), **inputs)
result = run(CalculationFactory('sirius.scf'), **inputs)

res = result['sirius'].get_content()
print("Result: \n{}".format(res))
