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
from aiida.common.folders import SandboxFolder
from aiida.common.datastructures import CalcJobState
from aiida.orm.utils.links import LinkTriple
from aiida.common import LinkType
from aiida_sirius.helpers.from_sirius import from_sirius_json
from aiida_sirius.helpers import get_pseudos_from_structure_and_path
from shutil import copyfile
import json
import argparse
import yaml

parser = argparse.ArgumentParser()
parser.add_argument('--nodes', '-N', default=1, type=int)
parser.add_argument('--label', default='', type=str)
parser.add_argument('--desc', default='', type=str)
parser.add_argument('--ntasks-per-node', '-p', default=1, type=int)
parser.add_argument('--ntasks-per-core', default=12, type=int)
parser.add_argument('--time', '-t', default=60, type=float, help='time in minutes')

args = parser.parse_args()

sirius_config_fname = 'sirius.json'

assert os.path.exists(sirius_config_fname)
assert os.path.exists('nlcg.yaml')
# converters sirius_json to aiida provenance input
sirius_json = json.load(open(sirius_config_fname, 'r'))

# get code
computer = helpers.get_computer('localhost')
# code = helpers.get_code(entry_point='sirius.nlcg', computer=computer)
code = Code.get_from_string('sirius.nlcg@' + computer.get_name())

####################
# # Prepare inputs #
####################
SiriusParameters = DataFactory('sirius.scf')
StructureData = DataFactory('structure')
KpointsData = DataFactory('array.kpoints')
Dict = DataFactory('dict')
SinglefileData = DataFactory('singlefile')

NLCGParameters = DataFactory('sirius.nlcg')
parameters = SiriusParameters(sirius_json)
nlcgconfig = yaml.load(open('nlcg.yaml', 'r'))
nlcgconfig = {'System': nlcgconfig['System'],
              'CG': nlcgconfig['CG']}

nlcgparams = NLCGParameters(nlcgconfig)

structure, magnetization, kpoints = from_sirius_json(sirius_json)
pseudos = get_pseudos_from_structure_and_path(structure, path='./')

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
            'output_filename': 'sirius.nlcg.out',
            'resources': comp_resources,
            'withmpi': True,
            'max_wallclock_seconds': -1
        },
        'label': args.label
    },
    'pseudos': pseudos
}
nlcgcalc = CalculationFactory('sirius.nlcg')
calc = nlcgcalc(inputs)

with SandboxFolder() as sandbox_folder:
    calc_info, script_filename = calc.presubmit(sandbox_folder)
    calc_info.uuid = calc.node.uuid
# calc_info = calc.prepare_for_submission(folder=None)
from aiida.engine.daemon import execmanager
with computer.get_transport() as transport:

    calc_info, script_filename = execmanager.upload_calculation(calc.node,
                                                                transport,
                                                                calc_info, script_filename=script_filename)
    # dummy submit
    job_id = -1
    calc.node.set_job_id(job_id)

    # copy stdout to workdir instead of running the actual calculation
    remote_workdir = calc.node.attributes['remote_workdir']
    copyfile('sirius.nlcg.out', os.path.join(remote_workdir, 'sirius.nlcg.out'))

    calc.node.set_state(CalcJobState.RETRIEVING)
    execmanager.retrieve_calculation(calc.node,
                                     transport,
                                     retrieved_temporary_folder=None)
    calc.node.set_state(CalcJobState.PARSING)
    execmanager.parse_results(calc)
    for out in calc.outputs:
        calc.outputs[out].store()
    calc.kill()
