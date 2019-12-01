from voluptuous import Optional, Schema, Any, Coerce, Range, All, Required
from aiida.orm import Dict


def get_sirius_md_schema():
    """this is for input.yml"""
    kolafa = {Required('type'): Any('kolafa'),
              Required('order'): All(int, Range(min=3, max=20))}
    niklasson_wf = {Required('type'): Any('niklasson_wf'),
                    Required('order'): All(int, Range(min=3, max=9))}
    plain = {Required('type'): Any('plain')}
    parameters = {Required('method', default=plain): Any(kolafa, niklasson_wf, plain),
                  Required('solver'): Any('ot', 'scf', 'mvp2'),
                  Optional('maxiter', default=30): All(int, Range(min=1)),
                  Optional('potential_tol', default=1e-6): All(float, Range(min=1e-14)),
                  Optional('energy_tol', default=1e-6): All(float, Range(min=1e-14)),
                  Optional('dt', default=1): All(Coerce(float), Range(min=0)),
                  Optional('N', default=100): All(int, Range(min=1))}

    return Schema(parameters)


class SiriusMDParameters(Dict):
    """SiriusMD, e.g. velocity verlet"""

    schema = get_sirius_md_schema()

    def __init__(self, dict=None, **kwargs):
        """Constructor for the data class

        Usage: ``SiriusMDParameters(dict=params)``

        :param parameters_dict: dictionary with commandline parameters
        :param type parameters_dict: dict

        """
        dict = self.validate(dict)
        super(SiriusMDParameters, self).__init__(dict=dict, **kwargs)

    def validate(self, parameters_dict):
        """Validate command line options.

        Uses the voluptuous package for validation. Find out about allowed keys using::

            print(SiriusMDParameters).schema.schema

        :param parameters_dict: dictionary with commandline parameters
        :param type parameters_dict: dict
        :returns: validated dictionary
        """
        return SiriusMDParameters.schema(parameters_dict)

    def __str__(self):
        """String representation of node.

        Append values of dictionary to usual representation. E.g.::

            uuid: b416cbee-24e8-47a8-8c11-6d668770158b (pk: 590)
            {'ignore-case': True}

        """
        string = super(SiriusMDParameters, self).__str__()
        string += "\n" + str(self.get_dict())
        return string
