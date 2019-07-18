# -*- coding: utf-8 -*-
"""
Parsers provided by aiida_sirius.

Register parsers via the "aiida.parsers" entry point in setup.json.
"""
from __future__ import absolute_import

from aiida.engine import ExitCode
from aiida.parsers.parser import Parser
from aiida.plugins import CalculationFactory, DataFactory
import json


SiriusCalculation = CalculationFactory('sirius.scf')
Dict = DataFactory('dict')


class SiriusSCFParser(Parser):
    """
    Parser class for parsing output of calculation.
    """

    def __init__(self, node):
        """
        Initialize Parser instance

        Checks that the ProcessNode being passed was produced by a SiriusCalculation.

        :param node: ProcessNode of calculation
        :param type node: :class:`aiida.orm.ProcessNode`
        """
        from aiida.common import exceptions
        super(SiriusSCFParser, self).__init__(node)
        if not issubclass(node.process_class, SiriusCalculation):
            raise exceptions.ParsingError("Can only parse SiriusCalculation")

    def parse(self, **kwargs):
        """
        Parse outputs, store results in database.

        :returns: an exit code, if parsing fails (or nothing if parsing succeeds)
        """
        from aiida.orm import SinglefileData

        output_filename = self.node.get_option('output_filename')
        print('output_filename (PARSER):', output_filename)

        # Check that folder content is as expected
        files_retrieved = self.retrieved.list_object_names()
        files_expected = [output_filename, 'output.json']
        # Note: set(A) <= set(B) checks whether A is a subset of B
        # this will fail if calcuation did not converge
        if not set(files_expected) <= set(files_retrieved):
            self.logger.error("Found files '{}', expected to find '{}'".format(
                files_retrieved, files_expected))
            return self.exit_codes.ERROR_MISSING_OUTPUT_FILES

        # add output file
        self.logger.info("Parsing '{}'".format(output_filename))
        with self.retrieved.open(output_filename, 'rb') as handle:
            output_node = SinglefileData(file=handle)
        with self.retrieved.open('output.json', 'r') as handle:
            result_json = json.load(handle)
        self.out('sirius', output_node)
        self.out('output', Dict(dict=result_json))

        if not result_json['ground_state']['converged']:
            return self.exit_codes.ERROR_NOT_CONVERGED


        return ExitCode(0)
