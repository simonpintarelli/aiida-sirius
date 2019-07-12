"""
Calculations provided by aiida_sirius.

Register calculations via the "aiida.calculations" entry point in setup.json.
"""
from __future__ import absolute_import

import six

from aiida.common import datastructures
from aiida.engine import CalcJob
from aiida.orm import SinglefileData
from aiida.plugins import DataFactory

SiriusParameters = DataFactory('sirius')


class SiriusCalculation(CalcJob):
    """
    AiiDA calculation plugin wrapping the diff executable.

    Simple AiiDA plugin wrapper for 'diffing' two files.
    """

    @classmethod
    def define(cls, spec):
        """Define inputs and outputs of the calculation."""
        # yapf: disable
        super(SiriusCalculation, cls).define(spec)
        spec.input('metadata.options.resources', valid_type=dict, default={'num_machines': 1, 'num_mpiprocs_per_machine': 1})
        spec.input('metadata.options.parser_name', valid_type=six.string_types, default='sirius')
        spec.input('metadata.options.output_filename', valid_type=six.string_types, default='output.json')
        spec.input('sirius_config', valid_type=SinglefileData, help='sirius.json config')
        spec.output('sirius', valid_type=SinglefileData, help='diff between file1 and file2.')

        spec.exit_code(100, 'ERROR_MISSING_OUTPUT_FILES', message='Calculation did not produce all expected output files.')


    def prepare_for_submission(self, folder):
        """
        Create input files.

        :param folder: an `aiida.common.folders.Folder` where the plugin should temporarily place all files needed by
            the calculation.
        :return: `aiida.common.datastructures.CalcInfo` instance
        """
        codeinfo = datastructures.CodeInfo()
        codeinfo.cmdline_params = self.inputs.parameters.cmdline_params(
            file1_name=self.inputs.file1.filename,
            file2_name=self.inputs.file2.filename)
        codeinfo.code_uuid = self.inputs.code.uuid
        codeinfo.stdout_name = self.metadata.options.output_filename
        codeinfo.withmpi = self.inputs.metadata.options.withmpi

        # Prepare a `CalcInfo` to be returned to the engine
        calcinfo = datastructures.CalcInfo()
        calcinfo.codes_info = [codeinfo]
        calcinfo.local_copy_list = [
            (self.inputs.sirius_config.uuid, self.inputs.sirius_config.filename, self.inputs.sirius_config.filename)
        ]
        calcinfo.retrieve_list = [self.metadata.options.output_filename]

        return calcinfo
