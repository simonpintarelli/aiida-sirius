[![Build Status](https://travis-ci.org/simonpintarelli/aiida-sirius.svg?branch=master)](https://travis-ci.org/simonpintarelli/aiida-sirius)
[![Coverage Status](https://coveralls.io/repos/github/simonpintarelli/aiida-sirius/badge.svg?branch=master)](https://coveralls.io/github/simonpintarelli/aiida-sirius?branch=master)
[![Docs status](https://readthedocs.org/projects/aiida-sirius/badge)](http://aiida-sirius.readthedocs.io/)
[![PyPI version](https://badge.fury.io/py/aiida-sirius.svg)](https://badge.fury.io/py/aiida-sirius)

# aiida-sirius

AiiDA plugin for the SIRIUS library

This plugin is the default output of the
[AiiDA plugin cutter](https://github.com/aiidateam/aiida-plugin-cutter),
intended to help developers get started with their AiiDA plugins.

## Features

TODO

## Installation

```shell
pip install aiida-sirius
verdi quicksetup  # better to set up a new profile
verdi plugin list aiida.calculations  # should now show your calclulation plugins
```

## Usage

Here goes a complete example of how to submit a test calculation using this plugin.

A quick demo of how to submit a calculation:

```shell
The plugin also includes verdi commands to inspect its data types:
```shell
verdi data sirius list
verdi data sirius export <PK>
```

## Development

```shell
git clone https://github.com/simonpintarelli/aiida-sirius .
cd aiida-sirius
pip install -e .[pre-commit,testing]  # install extra dependencies
pre-commit install  # install pre-commit hooks
pytest -v  # discover and run all tests
```

See the [developer guide](http://aiida-sirius.readthedocs.io/en/latest/developer_guide/index.html) for more information.

## License

MIT


## Contact

simon.pintarelli@cscs.ch
