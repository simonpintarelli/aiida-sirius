import spglib
import numpy as np

def irreducible_kpoints(structure, kpoints):
    """use spglib to compute number of irreducible k-points.

    Keyword arguments:
    structure -- aiida structure object
    kpoints -- aiida kpoint object
    Returns:
    nr      -- number of irreducible k-points
    mapping -- spglib mapping
    grid    -- spglib grid
    """
    pymatgen_st = structure.get_pymatgen()

    # build indicator array
    # list of atom symbols (string)
    atom_symbols = np.array([str(site.specie) for site in pymatgen_st.sites])

    # convert to indicators array
    indicators = np.zeros(len(atom_symbols))
    for i, symbol in enumerate(set(atom_symbols)):
        indicators[atom_symbols == symbol] = i

    rpos = [site.frac_coords for site in pymatgen_st.sites]
    cell = (pymatgen_st.lattice.matrix, rpos, indicators)
    mapping, grid = spglib.get_ir_reciprocal_mesh(kpoints.attributes['mesh'],
                                                  cell, is_shift=kpoints.attributes['offset'])

    return len(np.unique(mapping)), mapping, grid
