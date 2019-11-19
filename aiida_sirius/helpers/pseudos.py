import glob
import os

from aiida.orm.nodes.data import UpfData


def get_pseudos_from_structure_and_path(structure, path='./'):
    """
    Given a structure and a path where UPF files are supposed to be located, load
    upf files and return those contained in the structure


    :raise aiida.common.MultipleObjectsError: if more than one UPF for the same element is
       found in the group.
    :raise aiida.common.NotExistent: if no UPF for an element  is
       found in the group.
    """
    from aiida.common.exceptions import NotExistent, MultipleObjectsError

    # load all pseudos
    pseudo_files = ( set(glob.glob(os.path.join(path, '*UPF')))
                   | set(glob.glob(os.path.join(path, '*upf')))
                   | set(glob.glob(os.path.join(path, '*Upf'))))
    pseudos = {}
    for pp_file in pseudo_files:
        upf = UpfData(file=os.path.abspath(pp_file))
        if upf.element in pseudos:
            raise MultipleObjectsError(
                "More than one UPF for element {} found in "
                "{}".format(upf.element, path))

        pseudos[upf.element] = upf

    pseudo_list = {}
    for kind in structure.kinds:
        symbol = kind.symbol
        try:
            pseudo_list[kind.name] = pseudos[kind.name]
        except KeyError:
            raise NotExistent("No UPF for element {} found in path {}".format(
                symbol, path))

    return pseudo_list
