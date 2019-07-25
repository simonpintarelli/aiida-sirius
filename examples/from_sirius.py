from aiida.orm import StructureData, Dict
from aiida.plugins import DataFactory
from aiida.common.constants import bohr_to_ang
import numpy as np

KpointsData = DataFactory('array.kpoints')

def to_list(x):
    return [list(xi) for xi in x]


def read_magnetization(unit_cell_atoms):
    def get_mag(pos_mag):
        """
        returns [0, 0, 0] if not specified
        """
        mag = pos_mag[3:]
        if np.size(mag) == 0:
            return np.array([0, 0, 0])
        else:
            return mag
    magnetization = {}
    for atom_type in unit_cell_atoms:
        mag = [get_mag(lpos) for lpos in unit_cell_atoms[atom_type]]
        magnetization[atom_type] = mag
    return magnetization


def from_sirius_json(sirius_json):
    """Create input provenance from sirius_json. Assuming quantities
    are given in atomic units!

    Returns structure (unit_cell, sites) and magnetization

    Keyword Arguments:
    sirius_json -- sirius_json (as dict)

    Returns:
    - StructureData
    - magnetization dictionary
    - kpoint

    """
    sirius_unit_cell = sirius_json['unit_cell']

    if 'lattice_vectors_scale' in sirius_unit_cell:
        lattice_vectors_scale = sirius_unit_cell['lattice_vectors_scale']
    else:
        lattice_vectors_scale = 1

    cell_angstrom = np.array(sirius_unit_cell['lattice_vectors']) * lattice_vectors_scale * bohr_to_ang

    magnetization = read_magnetization(sirius_unit_cell['atoms'])

    # get kpoints
    kpoints = KpointsData()
    if 'vk' in sirius_json['parameters']:
        kpoints.set_kpoints(sirius_json['parameters']['vk'])
    else:
        ngridk = sirius_json['parameters']['ngridk']
        kpoints.set_kpoints_mesh(ngridk)

    s = StructureData(cell=to_list(cell_angstrom))
    if 'atom_coordinate_units' in sirius_unit_cell:
        if sirius_unit_cell['atom_coordinate_units'] in ['A', 'a.u.', 'au']:
            # atom positions are already given in angstrom, nothing to convert
            for atom_type in sirius_unit_cell['atoms']:
                for lposmag in sirius_unit_cell['atoms'][atom_type]:
                    lpos = np.array(lposmag[:3])
                    s.append_atom(position=tuple(lpos), symbols=atom_type)
        else:
            raise ValueError('invalid entry for atom_coordinate_units')
    else:
        # atom positions are given in relative coordinates
        for atom_type in sirius_unit_cell['atoms']:
            for lposmag in sirius_unit_cell['atoms'][atom_type]:
                lpos = np.array(lposmag[:3])
                apos = np.dot(cell_angstrom.T, lpos)
                s.append_atom(position=tuple(apos), symbols=atom_type)

    return s, magnetization, kpoints
