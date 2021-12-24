from .scf_base import SiriusBaseCalculation, add_cell_kpoints_mag_to_sirius
from ..data.sirius_options import sirius_options
from voluptuous import Schema
from aiida.plugins import DataFactory
from aiida.common import datastructures
import tempfile
import json
import six

NLCGParameters = DataFactory('sirius.py.nlcg')
SinglefileData = DataFactory('singlefile')
ArrayData = DataFactory('array')


class NLCGCPPCalculation(SiriusBaseCalculation):
    @classmethod
    def define(cls, spec):
        super(NLCGCPPCalculation, cls).define(spec)
        spec.input('metadata.options.parser_name', valid_type=six.string_types, default='sirius.cpp.nlcg')
        spec.input('metadata.options.output_filename', valid_type=six.string_types, default='sirius.cpp.nlcg.out')
        spec.output('nlcg', valid_type=SinglefileData)
        spec.output('cg_history', valid_type=ArrayData)

    def prepare_for_submission(self, folder):
        """
        Create input files.

        :param folder: an `aiida.common.folders.Folder` where the plugin should temporarily place all files needed by
            the calculation.
        :return: `aiida.common.datastructures.CalcInfo` instance
        """
        codeinfo = datastructures.CodeInfo()
        output_filename = self.metadata.options.output_filename
        codeinfo.code_uuid = self.inputs.code.uuid
        codeinfo.stdout_name = self.metadata.options.output_filename
        codeinfo.withmpi = self.inputs.metadata.options.withmpi

        # with config from input
        structure = self.inputs.structure
        kpoints = self.inputs.kpoints
        magnetization = self.inputs.magnetization

        sirius_json = self.inputs.sirius_config.get_dict()
        sirius_json = add_cell_kpoints_mag_to_sirius(sirius_json, structure,
                                                     magnetization, kpoints)
        # TODO check schema
        Schema(sirius_options)(sirius_json)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as sirius_tmpfile:
            # insert Pseudopotentials directly into json
            sirius_json = self._read_pseudos(sirius_json)
            # dump to file
            json.dump(sirius_json, sirius_tmpfile)
        sirius_config = SinglefileData(file=sirius_tmpfile.name)
        sirius_config.store()

        # Prepare a `CalcInfo` to be returned to the engine
        calcinfo = datastructures.CalcInfo()
        calcinfo.codes_info = [codeinfo]
        calcinfo.local_copy_list = [
            (sirius_config.uuid, sirius_config.filename, 'sirius.json')

        ]
        calcinfo.retrieve_list = [self.metadata.options.output_filename, 'nlcg.out', 'nlcg.json']

        return calcinfo
