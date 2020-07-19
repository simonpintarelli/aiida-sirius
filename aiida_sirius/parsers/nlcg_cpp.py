# -*- coding: utf-8 -*-
"""
Parsers provided by aiida_sirius.

Register parsers via the "aiida.parsers" entry point in setup.json.
"""
from __future__ import absolute_import

from aiida.engine import ExitCode
from aiida.parsers.parser import Parser
from aiida.plugins import CalculationFactory, DataFactory

import numpy as np
import re
import json

NLCGCPPCalculation = CalculationFactory('sirius.cpp.nlcg')
Dict = DataFactory('dict')
Array = DataFactory('array')


def parse_cg_history(fh):
    """Parse sirius.py.nlcg output
    """

    rgx = '\s*([0-9]+)\s+([0-9]\+\-\.)\s+([0-9]\+\-\.)'
    out = []

    for line in fh.readlines():
        match = re.match(rgx, line.strip())
        if match:
            i = int(match.group(1))
            F = int(match.group(2))
            res = int(match.group(3))
            out.append((i, F, res))
    return out


class NLCGCPPParser(Parser):
    """
    Parser class for parsing output of calculation (cpp, sirius.py.nlcg miniapp).
    """

    def __init__(self, node):
        """
        Initialize Parser instance

        Checks that the ProcessNode being passed was produced by a SiriusCalculation.

        :param node: ProcessNode of calculation
        :param type node: :class:`aiida.orm.ProcessNode`
        """
        from aiida.common import exceptions
        super(NLCGCPPParser, self).__init__(node)
        if not issubclass(node.process_class, NLCGCPPCalculation):
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
        files_expected = [output_filename, 'nlcg.out']
        # Note: set(A) <= set(B) checks whether A is a subset of B
        # this will fail if calcuation did not converge
        if not set(files_expected) <= set(files_retrieved):
            self.logger.error("Found files '{}', expected to find '{}'".format(
                files_retrieved, files_expected))
            return self.exit_codes.ERROR_MISSING_OUTPUT_FILES

        # add output file
        self.logger.info("Storing '{}'".format(output_filename))
        with self.retrieved.open(output_filename, 'rb') as handle:
            stdout_node = SinglefileData(file=handle)

        self.logger.info("Parsing '{}'".format('nlcg.out'))
        with self.retrieved.open('nlcg.out', 'rb') as handle:
            output_node = SinglefileData(file=handle)

        with self.retrieved.open('nlcg.out', 'r') as handle:
            cg_history = parse_cg_history(handle)

        cg_history = np.array(cg_history)
        cg_history_node = Array()
        cg_history_node.set_array('cg_history', array=cg_history)

        self.out('stdout', stdout_node)
        self.out('nlcg', output_node)
        self.out('cg_history', cg_history_node)

        return ExitCode(0)
