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
import json

# get code
computer = helpers.get_computer()
code = helpers.get_code(entry_point='sirius', computer=computer)

# Prepare input parameters
DiffParameters = DataFactory('sirius')
parameters = DiffParameters({'ignore-case': True})

SinglefileData = DataFactory('singlefile')
# file1 = SinglefileData(
#     file=os.path.join(tests.TEST_DIR, "input_files", 'file1.txt'))
# file2 = SinglefileData(
#     file=os.path.join(tests.TEST_DIR, "input_files", 'file2.txt'))

config = json.load(open('sirius.json', 'r'))
ps_C = json.load(open('C.json', 'r'))
config['unit_cell']['atom_files']['C'] = json.dumps(ps_C)

with open('sirius-final.json', 'w') as fh:
    json.dump(config, fh)



# TODO: assemble sirius_config
sirius_config = SinglefileData(file=os.path.abspath('sirius-final.json'))

# set up calculation
inputs = {
    'code': code,
    'parameters': parameters,
    'sirius_config': sirius_config,
    'metadata': {
        'description': "Test job submission with the aiida_sirius plugin",
    },
}

# Note: in order to submit your calculation to the aiida daemon, do:
# from aiida.engine import submit
# future = submit(CalculationFactory('sirius'), **inputs)
result = run(CalculationFactory('sirius'), **inputs)

computed_diff = result['sirius'].get_content()
print("Computed diff between files: \n{}".format(computed_diff))
