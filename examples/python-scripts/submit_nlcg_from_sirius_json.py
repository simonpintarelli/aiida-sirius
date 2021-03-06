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

parser = argparse.ArgumentParser()
parser.add_argument('--computer', '-c', default='daint-gpu')
parser.add_argument('--nodes', '-N', default=1, type=int)
parser.add_argument('--ntasks-per-node', '-p', default=1, type=int)
parser.add_argument('--ntasks-per-core', '-n', default=1, type=int)
parser.add_argument('--time', '-t', default=60, type=float, help='time in minutes')


args = parser.parse_args()

# converters sirius_json to aiida provenance input
from from_sirius import from_sirius_json

sirius_json = json.load(open('sirius.json', 'r'))

# get code
computer = helpers.get_computer(args.computer)
# code = helpers.get_code(entry_point='sirius.py.nlcg', computer=computer)
code = Code.get_from_string('sirius.py.nlcg@' + computer.get_name())

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

####################
# # Prepare inputs #
####################
SiriusParameters = DataFactory('sirius.scf')
StructureData = DataFactory('structure')
KpointsData = DataFactory('array.kpoints')
Dict = DataFactory('dict')
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

structure, magnetization, kpoints = from_sirius_json(sirius_json)

####################################################
# # Warning pseudopotentials are taken from aiida! #
####################################################
pseudos = get_pseudos_from_structure(structure, 'normcons')

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
        'description': "Test job submission with the aiida_sirius plugin",
        'options': {
            'resources': comp_resources,
            'withmpi': True,
            'max_wallclock_seconds': int(args.time * 60)
        }
    },
    'pseudos': pseudos
}

# Note: in order to submit your calculation to the aiida daemon, do:
# from aiida.engine import submit
# future = submit(CalculationFactory('sirius'), **inputs)
calc = CalculationFactory('sirius.py.nlcg')
result = submit(calc, **inputs)
