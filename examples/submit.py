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

# Prepare input parameters
SiriusParameters = DataFactory('sirius')
StructureData = DataFactory('structure')
parameters = SiriusParameters({'control': {},
                               'iterative_solver': {}})
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
result = run(CalculationFactory('sirius'), **inputs)

res = result['sirius'].get_content()
print("Result: \n{}".format(res))
