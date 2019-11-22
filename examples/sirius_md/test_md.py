# -*- coding: utf-8 -*-
"""Submit a test calculation on localhost.

Usage: verdi run submit.py
"""

from aiida_sirius import helpers
from aiida.plugins import DataFactory, CalculationFactory
from aiida.engine import run, submit
from aiida.orm import Code
from aiida.orm.nodes.data.upf import get_pseudos_from_structure
import json
import yaml
computer = helpers.get_computer('ault-intel')
code = Code.get_from_string('sirius.md@' + computer.get_name())

# Prepare input parameters
SiriusMDParameters = DataFactory('sirius.md')
SiriusParameters = DataFactory('sirius.scf')
SinglefileData = DataFactory('singlefile')

md_parameters = SiriusMDParameters(yaml.load(open('input.yml', 'r'))['parameters'])

# load SIRIUS parameters from json
sirius_json = json.load(open('sirius.json', 'r'))

# extract structure, magnetization, kppoints (for the sake of AiiDA provenance)
structure, magnetization, kpoints = helpers.from_sirius_json(sirius_json)

# set up calculation

inputs = {
    'code': code,
    'sirius_config': SiriusParameters(sirius_json),
    'sirius_md_params': md_parameters,
    'structure': structure,
    'kpoints': kpoints,
    'metadata': {
        'options': {
            'withmpi': True,
            'prepend_text': '#SBATCH --nodelist=ault02',
            'max_wallclock_seconds': 3600
        },
    },
    'pseudos': get_pseudos_from_structure(structure, 'sg15_pz')
}

calc = CalculationFactory('sirius.md')
# result = submit(calc, **inputs)
submit(calc, **inputs)

# res = result['sirius'].get_content()
# print("Result: \n{}".format(res))
