"""
Calculations provided by aiida_sirius.

Register calculations via the "aiida.calculations" entry point in setup.json.
"""
from __future__ import absolute_import

import json
import os
import tempfile
from copy import deepcopy

import numpy as np
import six

from aiida.common import datastructures
from aiida.common.constants import bohr_to_ang
from aiida.engine import CalcJob
from aiida.orm import StructureData, UpfData
from aiida.plugins import DataFactory
import tempfile

from ..upf_to_json import upf_to_json

SiriusParameters = DataFactory('sirius.scf')
SinglefileData = DataFactory('singlefile')
KpointsData = DataFactory('array.kpoints')
Dict = DataFactory('dict')

SIRIUS_JSON = {
    "control": {
        "processing_unit": "gpu",
        "std_evp_solver_type": "lapack",
        "gen_evp_solver_type": "lapack",
        "verbosity": 1,
    },
    "parameters": {
        "electronic_structure_method": "pseudopotential",
        "xc_functionals": ["XC_GGA_X_PBE", "XC_GGA_C_PBE"],
        "smearing_width": 0.025,
        "use_symmetry": True,
        "num_mag_dims": '<MISSING>',
        "gk_cutoff": 6.0,
        "pw_cutoff": 27.00,
        "energy_tol": 1e-8,
        "potential_tol": 1e-8,
        "num_dft_iter": 100,
    },
    "iterative_solver": {
        "type": "davidson",
        "min_occupancy": 1e-5
    },
    "unit_cell": {
        "lattice_vectors": [],
        "atom_coordinate_units": "au",
        "atom_types": [""],
        "atom_files": {},
        "atoms": {
        }
    },
    "mixer": {
        "beta": "<MISSING>",
        "type": "broyden1",
        "max_history": 8
    }
}


def make_sirius_json(structure, kpoints, magnetization):
    """
    Keyword Arguments:
    structure -- structure
    pseudos   -- dictionary of UpfData
    """
    sirius_cell, sirius_pos = read_structure(structure, magnetization.get_dict())
    sirius_json = deepcopy(SIRIUS_JSON)
    sirius_json['unit_cell']['lattice_vectors'] = sirius_cell
    sirius_json['unit_cell']['atom_types'] = list(sirius_pos.keys())
    sirius_json['unit_cell']['atoms'] = sirius_pos
    sirius_json['parameters']['ngridk'] = kpoints.attributes['mesh']
    sirius_json['parameters']['shiftk'] = kpoints.attributes['offset']

    return sirius_json


def read_structure(structure, magnetization):
    """
    Convert obj of type `StructureData` to sirius input format (e.g. a dictionary)
    Return:
    - cell
    - atomic coordinates
    """
    cell = structure.cell
    # cell in atomic units
    cell = np.array(cell) / bohr_to_ang
    # convert back to list of list
    cell = [list(x) for x in cell]
    sites = structure.sites
    atom_types = set([x.kind_name for x in sites])
    atomic_coordinates = {}
    for atom_type in atom_types:
        ltypes = list(filter(lambda x: x.kind_name == atom_type, sites))
        lpos = np.array([x.position for x in ltypes]) / bohr_to_ang
        try:
            lmag = np.array(magnetization[atom_type])
        except KeyError:
            lmag = np.zeros_like(lpos)
        lpos_with_mag = np.concatenate((lpos, lmag), axis=1)
        atomic_coordinates[atom_type] = [list(x) for x in lpos_with_mag]
    return cell, atomic_coordinates


class SiriusBaseCalculation(CalcJob):
    """
    AiiDA calculation plugin wrapping the diff executable.

    Simple AiiDA plugin wrapper for 'diffing' two files.
    """

    @classmethod
    def define(cls, spec):
        """Define inputs and outputs of the calculation."""
        # yapf: disable
        super(SiriusBaseCalculation, cls).define(spec)
        spec.input('metadata.options.resources', valid_type=dict, default={'num_machines': 1, 'num_mpiprocs_per_machine': 1})
        spec.input('structure', valid_type=StructureData, help='The input structure')
        spec.input('kpoints', valid_type=KpointsData, help='kpoints')
        spec.input('sirius_config', valid_type=SiriusParameters, help='sirius parameters')
        spec.input('magnetization', valid_type=Dict, default=Dict(dict={}))
        spec.input_namespace('pseudos', valid_type=UpfData, dynamic=True,
                             help='A mapping of `UpfData` nodes onto the kind name to which they should apply.')

    def _read_pseudos(self, sirius_json):
        # parse pseudos
        for atom_label in self.inputs.pseudos:
            upf = self.inputs.pseudos[atom_label]
            with upf.open() as fh:
                upf_json = upf_to_json(fh.read(), fname=upf.filename)
            sirius_json['unit_cell']['atom_files'][atom_label] = json.dumps(upf_json)
        return sirius_json


class SiriusSCFCalculation(SiriusBaseCalculation):
    """
    AiiDA calculation plugin wrapping the diff executable.

    Simple AiiDA plugin wrapper for 'diffing' two files.
    """

    @classmethod
    def define(cls, spec):
        """Define inputs and outputs of the calculation."""
        # yapf: disable
        super(SiriusSCFCalculation, cls).define(spec)
        spec.input('metadata.options.parser_name', valid_type=six.string_types, default='sirius.scf')
        spec.input('metadata.options.output_filename', valid_type=six.string_types, default='sirius.scf.out')
        spec.output('sirius', valid_type=SinglefileData, help='standard output')
        spec.output('output', valid_type=Dict, help='sirius.scf json output')
        spec.exit_code(100, 'ERROR_MISSING_OUTPUT_FILES', message='Calculation did not produce all expected output files.')
        spec.exit_code(201, 'ERROR_NOT_CONVERGED', message='Calculation did not converge.')


    def prepare_for_submission(self, folder):
        """
        Create input files.

        :param folder: an `aiida.common.folders.Folder` where the plugin should temporarily place all files needed by
            the calculation.
        :return: `aiida.common.datastructures.CalcInfo` instance
        """
        codeinfo = datastructures.CodeInfo()
        output_filename = self.metadata.options.output_filename
        codeinfo.cmdline_params = ['--output=output.json']
        codeinfo.code_uuid = self.inputs.code.uuid
        codeinfo.stdout_name = self.metadata.options.output_filename
        codeinfo.withmpi = self.inputs.metadata.options.withmpi

        # with config from input
        structure = self.inputs.structure
        kpoints = self.inputs.kpoints
        magnetization = self.inputs.magnetization
        sirius_json = make_sirius_json(structure, kpoints, magnetization)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as sirius_tmpfile:
            sirius_json = self._read_pseudos(sirius_json)
            sirius_tmpfile_name = sirius_tmpfile.name
            # merge with settings given from outside
            sirius_json = {**sirius_json, **self.inputs.sirius_config.get_dict()}
            # dump to file
            json.dump(sirius_json, sirius_tmpfile)
        sirius_config = SinglefileData(file=sirius_tmpfile_name)
        sirius_config.store()

        # Prepare a `CalcInfo` to be returned to the engine
        calcinfo = datastructures.CalcInfo()
        calcinfo.codes_info = [codeinfo]
        calcinfo.local_copy_list = [
            (sirius_config.uuid, sirius_config.filename, 'sirius.json')
        ]
        calcinfo.retrieve_list = [self.metadata.options.output_filename, 'output.json']

        return calcinfo
