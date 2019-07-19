from .scf_base import SiriusBaseCalculation, make_sirius_json
from aiida.plugins import DataFactory
from aiida.common import datastructures
import tempfile
import json
import yaml

NLCGParameters = DataFactory('nlcg')
SinglefileData = DataFactory('singlefile')

class NLCGCalculation(SiriusBaseCalculation):
    @classmethod
    def define(cls, spec):
        super(NLCGCalculation, cls).define(spec)
        spec.input('NLCGParams', valid_type=NLCGParameters, help='NLCG Parameters')

    def prepare_for_submission(self, folder):
        """
        Create input files.

        :param folder: an `aiida.common.folders.Folder` where the plugin should temporarily place all files needed by
            the calculation.
        :return: `aiida.common.datastructures.CalcInfo` instance
        """
        codeinfo = datastructures.CodeInfo()
        output_filename = self.metadata.options.output_filename
        # TODO: adpat to NLCG
        codeinfo.cmdline_params = ['--output=output.json']
        codeinfo.code_uuid = self.inputs.code.uuid
        codeinfo.stdout_name = self.metadata.options.output_filename
        codeinfo.withmpi = self.inputs.metadata.options.withmpi

        # with config from input
        structure = self.inputs.structure
        kpoints = self.inputs.kpoints
        sirius_json = make_sirius_json(structure, kpoints)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as sirius_tmpfile:
            sirius_json = self._read_pseudos(sirius_json)
            sirius_tmpfile_name = sirius_tmpfile.name
            # merge with settings given from outside
            sirius_json = {**sirius_json, **self.inputs.sirius_config.get_dict()}
            # dump to file
            json.dump(sirius_json, sirius_tmpfile)
        sirius_config = SinglefileData(file=sirius_tmpfile_name)
        sirius_config.store()

        # TODO prepare config.yaml for NLCG

        # Prepare a `CalcInfo` to be returned to the engine
        calcinfo = datastructures.CalcInfo()
        calcinfo.codes_info = [codeinfo]
        calcinfo.local_copy_list = [
            (sirius_config.uuid, sirius_config.filename, 'sirius.json')
        ]
        calcinfo.retrieve_list = [self.metadata.options.output_filename, 'output.json']

        return calcinfo
