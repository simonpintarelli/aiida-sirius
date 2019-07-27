from .scf_base import SiriusBaseCalculation, make_sirius_json
from aiida.plugins import DataFactory
from aiida.common import datastructures
import tempfile
import json
import yaml
import six

NLCGParameters = DataFactory('sirius.nlcg')
SinglefileData = DataFactory('singlefile')
ArrayData = DataFactory('array')

class NLCGCalculation(SiriusBaseCalculation):
    @classmethod
    def define(cls, spec):
        super(NLCGCalculation, cls).define(spec)
        spec.input('nlcgparams', valid_type=NLCGParameters, help='NLCG Parameters')
        spec.input('metadata.options.parser_name', valid_type=six.string_types, default='sirius.nlcg')
        spec.input('metadata.options.output_filename', valid_type=six.string_types, default='sirius.nlcg.out')
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
        # TODO: adpat to NLCG
        codeinfo.cmdline_params = ['--input=nlcg.yaml']
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
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as nlcg_yaml:
            out = yaml.dump(self.inputs.nlcgparams.get_dict())
            nlcg_tmpfile_name = nlcg_yaml.name
            nlcg_yaml.write(out)
        nlcg_config = SinglefileData(file=nlcg_tmpfile_name)
        nlcg_config.store()

        # Prepare a `CalcInfo` to be returned to the engine
        calcinfo = datastructures.CalcInfo()
        calcinfo.codes_info = [codeinfo]
        calcinfo.local_copy_list = [
            (sirius_config.uuid, sirius_config.filename, 'sirius.json'),
            (nlcg_config.uuid, nlcg_config.filename, 'nlcg.yaml')

        ]
        calcinfo.retrieve_list = [self.metadata.options.output_filename]

        return calcinfo
