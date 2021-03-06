# -*- coding: utf-8 -*-
"""
Data types provided by plugin

Register data types via the "aiida.data" entry point in setup.json.
"""

# You can directly use or subclass aiida.orm.data.Data
# or any other data type listed under 'verdi data'
from __future__ import absolute_import
from voluptuous import Schema
from aiida.orm import Dict
from .sirius_options import sirius_options


class SiriusParameters(Dict):
    """Command line options for sirius.scf.

    This class represents a python dictionary equivalent to the sirius.json file.
    """

    # # "voluptuous" schema  to add automatic validation
    # schema = Schema(sirius_options)

    # pylint: disable=redefined-builtin
    def __init__(self, dict=None, **kwargs):
        """
        Constructor for the data class

        Usage: ``SiriusParameters(dict=params)``

        :param params: dictionary with sirius.json
        """
        dict = self.validate(dict)
        super(SiriusParameters, self).__init__(dict=dict, **kwargs)

    def validate(self, parameters_dict):
        """Validate command line options.

        Uses the voluptuous package for validation. Find out about allowed keys using::

            print(SiriusParameters).schema.schema

        :param parameters_dict: dictionary with commandline parameters
        :param type parameters_dict: dict
        :returns: validated dictionary
        """
        # return SiriusParameters.schema(parameters_dict)
        # only validate mixer, control, iterative_solver since parameters, unit_cell are added afterwards
        validate_entries = set(parameters_dict.keys()).intersection(['control', 'mixer', 'iterative_solver'])
        params_to_validate = {x: parameters_dict[x] for x in validate_entries}
        validated = Schema({x: sirius_options[x] for x in validate_entries})(params_to_validate)
        return {**validated, **parameters_dict}

    def __str__(self):
        """String representation of node.
        """
        string = super(SiriusParameters, self).__str__()
        string += "\n" + str(self.get_dict())
        return string
