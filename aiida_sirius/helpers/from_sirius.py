from aiida.orm import StructureData, Dict
from aiida.plugins import DataFactory
import numpy as np

KpointsData = DataFactory('array.kpoints')
bohr_to_ang = 0.529177210903

def to_list(x):
    return [list(xi) for xi in x]


def read_magnetization(unit_cell_atoms):
    """Extract magnetization dictionary from sirius_json['unit_cell']['atoms'].

    Keyword Arguments:
    -- unit_cell_atoms: e.g. sirius_json['unit_cell']['atoms']

    Returns:
    -- magnetization dictionary as used in the provenance of the aiida_sirius plugin
    """
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


def sirius_to_aiida_structure(sirius_unit_cell):
    """Extracts aiida structure from the sirius['unit_cell'] json input.

    Keyword Arguments:
    -- sirius_unit_cell: sirius_json['unit_cell'] dictionary

    Returns:
    -- aiida_structure: object of type `aiida.orm.StructureData`

    """
    if 'lattice_vectors_scale' in sirius_unit_cell:
        lattice_vectors_scale = sirius_unit_cell['lattice_vectors_scale']
    else:
        lattice_vectors_scale = 1

    cell_angstrom = np.array(sirius_unit_cell['lattice_vectors']) * lattice_vectors_scale * bohr_to_ang

    structure = StructureData(cell=to_list(cell_angstrom))
    if 'atom_coordinate_units' in sirius_unit_cell:
        if sirius_unit_cell['atom_coordinate_units'] in ['A', 'a.u.', 'au']:
            # atom positions are already given in angstrom, nothing to convert
            for atom_type in sirius_unit_cell['atoms']:
                for lposmag in sirius_unit_cell['atoms'][atom_type]:
                    lpos = np.array(lposmag[:3])
                    if sirius_unit_cell['atom_coordinate_units'] in ['a.u.', 'au']:
                        structure.append_atom(position=tuple(lpos*bohr_to_ang), symbols=atom_type)
                    else:
                        structure.append_atom(position=tuple(lpos), symbols=atom_type)
        else:
            raise ValueError('invalid entry for atom_coordinate_units')
    else:
        # atom positions are given in relative coordinates
        for atom_type in sirius_unit_cell['atoms']:
            for lposmag in sirius_unit_cell['atoms'][atom_type]:
                lpos = np.array(lposmag[:3])
                apos = np.dot(cell_angstrom.T, lpos)
                structure.append_atom(position=tuple(apos), symbols=atom_type)
    return structure


def from_sirius_json(sirius_json):
    """Create input provenance from sirius_json. Assuming quantities
    are given in atomic units.

    Returns structure (unit_cell, sites) and magnetization

    Keyword Arguments:
    sirius_json -- sirius_json (as dict)

    Returns:
    - StructureData
    - magnetization dictionary
    - kpoint

    """
    sirius_unit_cell = sirius_json['unit_cell']

    magnetization = read_magnetization(sirius_unit_cell['atoms'])

    # get kpoints
    kpoints = KpointsData()
    if 'vk' in sirius_json['parameters']:
        kpoints.set_kpoints(sirius_json['parameters']['vk'])
    else:
        ngridk = sirius_json['parameters']['ngridk']
        kpoints.set_kpoints_mesh(ngridk)

    structure = sirius_to_aiida_structure(sirius_unit_cell)

    return structure, magnetization, kpoints
