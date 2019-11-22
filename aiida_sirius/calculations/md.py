from .scf_base import SiriusBaseCalculation, make_sirius_json
from aiida.plugins import DataFactory
from aiida.common import datastructures
import tempfile
import json
import yaml
import six

SiriusMDParameters = DataFactory('sirius.md')
SinglefileData = DataFactory('singlefile')
ArrayData = DataFactory('array')
List = DataFactory('list')

class SiriusMDCalculation(SiriusBaseCalculation):
    @classmethod
    def define(cls, spec):
        super(SiriusMDCalculation, cls).define(spec)
        spec.input('sirius_md_params', valid_type=SiriusMDParameters, help='MD Parameters')
        spec.input('metadata.options.parser_name', valid_type=six.string_types, default='sirius.md')
        spec.input('metadata.options.output_filename', valid_type=six.string_types, default='sirius.md.out')
        spec.output('md', valid_type=SinglefileData)
        spec.output('md_history', valid_type=List)

    def prepare_for_submission(self, folder):
        """
        Create input files.
        sirius.json,
        input.yml

        :param folder: an `aiida.common.folders.Folder` where the plugin should temporarily place all files needed by
            the calculation.
        :return: `aiida.common.datastructures.CalcInfo` instance
        """
        codeinfo = datastructures.CodeInfo()
        output_filename = self.metadata.options.output_filename
        codeinfo.cmdline_params = ['--input=input.yml']
        codeinfo.code_uuid = self.inputs.code.uuid
        codeinfo.stdout_name = self.metadata.options.output_filename
        codeinfo.withmpi = self.inputs.metadata.options.withmpi

        # with config from input
        structure = self.inputs.structure
        kpoints = self.inputs.kpoints
        magnetization = self.inputs.magnetization
        # sirius_json = make_sirius_json(self.inputs.sirius_config.get_dict()['parameters'],
        sirius_json = self.inputs.sirius_config.get_dict()
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as sirius_tmpfile:
            # insert Pseudopotentials directly into json
            sirius_json = self._read_pseudos(sirius_json)
            # dump to file
            json.dump(sirius_json, sirius_tmpfile)
        sirius_config = SinglefileData(file=sirius_tmpfile.name)
        sirius_config.store()
        # prepare YAML input for NLCG
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as sirius_md_yaml:
            out = yaml.dump({'parameters': self.inputs.sirius_md_params.get_dict()})
            md_tmpfile_name = sirius_md_yaml.name
            sirius_md_yaml.write(out)
        sirius_md_config = SinglefileData(file=md_tmpfile_name)
        sirius_md_config.store()

        # Prepare a `CalcInfo` to be returned to the engine
        calcinfo = datastructures.CalcInfo()
        calcinfo.codes_info = [codeinfo]
        calcinfo.local_copy_list = [
            (sirius_config.uuid, sirius_config.filename, 'sirius.json'),
            (sirius_md_config.uuid, sirius_md_config.filename, 'input.yml')

        ]
        calcinfo.retrieve_list = [self.metadata.options.output_filename, 'md_results.json']

        return calcinfo
