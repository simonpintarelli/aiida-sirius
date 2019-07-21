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
import json

NLCGCalculation = CalculationFactory('sirius.nlcg')
Dict = DataFactory('dict')
Array = DataFactory('array')


def parse_cg_history(fh):
    """Parse CG history

    Keyword Arguments:
    fh -- file handle

    Returns:
    a list of tuples:
    [e_1, ..., e_N]

    where:
    e_i = (i, F, resX, resf|eta)
    """
    import re
    # step    24 F: -26.34592024007 res: X,fn -6.84493e-04 -8.38853e-01
    # step   218 F: -60.51049737235 res: X,eta -4.43797e-12, -3.10230e-1
    out = []
    regx='\s*step\s*([0-9]+)\s*F:\s*(.*)res:\s*X,(?:fn|eta)(.*)[,]?\s+(.*)'
    for line in fh.readlines():
        # .strip() to remove newlines at the end
        match = re.match(regx, line.strip())
        if match:
            i = int(match.group(1))
            F = float(match.group(2))
            resX = float(match.group(3))
            resf = float(match.group(4))
            out.append((i, F, resX, resf))
    return out


class NLCGParser(Parser):
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
        super(NLCGParser, self).__init__(node)
        if not issubclass(node.process_class, NLCGCalculation):
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
        files_expected = [output_filename]
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
            # output_node.store()
        with self.retrieved.open(output_filename, 'r') as handle:
            cg_history = parse_cg_history(handle)

        cg_history = np.array(cg_history)
        cg_history_node = Array()
        cg_history_node.set_array('cg_history', array=cg_history)

        self.out('nlcg', output_node)
        self.out('cg_history', cg_history_node)

        return ExitCode(0)
