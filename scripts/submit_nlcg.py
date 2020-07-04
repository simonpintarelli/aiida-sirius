# -*- coding: utf-8 -*-
"""Submit a test calculation on daint-gpu

Usage: verdi run submit.py
"""

from __future__ import absolute_import
from __future__ import print_function
import os
from aiida_sirius import tests, helpers
from aiida.plugins import DataFactory, CalculationFactory
from aiida.engine import run, submit
from aiida.orm.nodes.data.upf import get_pseudos_from_structure
from aiida.orm import Code
import json
import argparse
import yaml

parser = argparse.ArgumentParser()
parser.add_argument('--computer', '-c', default='daint-gpu')
parser.add_argument('--nodes', '-N', default=1, type=int)
parser.add_argument('--label', default='', type=str)
parser.add_argument('--desc', default='', type=str)
parser.add_argument('--ntasks-per-node', '-p', default=1, type=int)
parser.add_argument('--ntasks-per-core', default=12, type=int)
parser.add_argument('--pseudos', default='normcons')
parser.add_argument('--time', '-t', default=60, type=float, help='time in minutes')
parser.add_argument('sirius_json')

args = parser.parse_args()

sirius_json = args.sirius_json

assert os.path.exists(sirius_json)
assert os.path.exists('nlcg.yaml')
# converters sirius_json to aiida provenance input
from aiida_sirius.helpers.from_sirius import from_sirius_json

sirius_json = json.load(open(sirius_json, 'r'))

# get code
computer = helpers.get_computer(args.computer)
# code = helpers.get_code(entry_point='sirius.py.nlcg', computer=computer)
code = Code.get_from_string('sirius.py.nlcg@' + computer.get_name())

####################
# # Prepare inputs #
####################
SiriusParameters = DataFactory('sirius.scf')
StructureData = DataFactory('structure')
KpointsData = DataFactory('array.kpoints')
Dict = DataFactory('dict')
SinglefileData = DataFactory('singlefile')

NLCGParameters = DataFactory('sirius.py.nlcg')
parameters = SiriusParameters(sirius_json)
nlcgconfig = yaml.load(open('nlcg.yaml', 'r'))
nlcgconfig = {'System': nlcgconfig['System'],
              'CG': nlcgconfig['CG']}

nlcgparams = NLCGParameters(nlcgconfig)

structure, magnetization, kpoints = from_sirius_json(sirius_json)
pseudos = get_pseudos_from_structure(structure, args.pseudos)

print('tasks_per_core', args.ntasks_per_core)
# 'num_cores_per_machine': 1,
comp_resources = {'num_mpiprocs_per_machine': args.ntasks_per_node,
                  'num_machines': args.nodes,
                  'num_cores_per_mpiproc': args.ntasks_per_core}

# set up calculation
inputs = {
    'code': code,
    'sirius_config': parameters,
    'structure': structure,
    'kpoints': kpoints,
    'nlcgparams': nlcgparams,
    'magnetization': Dict(dict=magnetization),
    'metadata': {
        'options': {
            'resources': comp_resources,
            'withmpi': True,
            'max_wallclock_seconds': int(args.time * 60)
        },
        'label': args.label
    },
    'pseudos': pseudos
}

# Note: in order to submit your calculation to the aiida daemon, do:
# from aiida.engine import submit
# future = submit(CalculationFactory('sirius'), **inputs)
calc = CalculationFactory('sirius.py.nlcg')
result = submit(calc, **inputs)
print(result.pk)
