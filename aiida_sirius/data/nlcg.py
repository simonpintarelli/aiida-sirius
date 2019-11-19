from voluptuous import Optional, Schema, Any, Coerce, Required, Any, Length

from aiida.orm import Dict

def get_nlcg_schema():
    """Using voluptuous to make sure that the config is valid and
    populate missing entries by their default values.
    """

    teter_precond = {Required('type'): Any('teter')}
    kinetic_precond = {Required('type'): Any('kinetic'),
                       Optional('eps', default=1e-3): Coerce(float)}
    identity_precond = {Required('type', default='identity'): Any('identity')}
    precond = Any(identity_precond, kinetic_precond, teter_precond)

    marzari = {Required('type'): Any('Marzari'),
               Optional('inner', default=2): int,
               Optional('fd_slope_check', default=False): bool}
    neugebaur = {Required('type'): Any('Neugebaur'), Optional('kappa', default=0.3): Coerce(float)}

    cg = {Required('CG'): {Required('method'): Any(marzari, neugebaur),
                           Optional('type', default='FR'): Any('FR', 'PR'),
                           Optional('tol', default=1e-9): Coerce(float),
                           Optional('maxiter', default=300): int,
                           Optional('restart', default=20): int,
                           Optional('nscf', default=4): int,
                           Optional('tau', default=0.1): Coerce(float),
                           Optional('precond'): precond,
                           Optional('callback_interval', default=50): int},
          Required('System'): {
              Required('T', default=300): Coerce(float),
              Required('smearing', default='fermi-dirac'): Any('fermi-dirac', 'gaussian-spline')
          }
    }

    return Schema(cg)


class NLCGParameters(Dict):
    """Non-linear CG parameters
    yaml config for nlcg.py
    """

    schema = get_nlcg_schema()

    # pylint: disable=redefined-builtin
    def __init__(self, dict=None, **kwargs):
        """Constructor for the data class

        Usage: ``NLCGParameters(dict=params)``

        :param parameters_dict: dictionary with commandline parameters
        :param type parameters_dict: dict

        """
        dict = self.validate(dict)
        super(NLCGParameters, self).__init__(dict=dict, **kwargs)

    def validate(self, parameters_dict):
        """Validate command line options.

        Uses the voluptuous package for validation. Find out about allowed keys using::

            print(NLCGParameters).schema.schema

        :param parameters_dict: dictionary with commandline parameters
        :param type parameters_dict: dict
        :returns: validated dictionary
        """
        return NLCGParameters.schema(parameters_dict)

    def __str__(self):
        """String representation of node.

        Append values of dictionary to usual representation. E.g.::

            uuid: b416cbee-24e8-47a8-8c11-6d668770158b (pk: 590)
            {'ignore-case': True}

        """
        string = super(NLCGParameters, self).__str__()
        string += "\n" + str(self.get_dict())
        return string
