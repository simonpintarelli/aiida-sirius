from voluptuous import Optional, Schema, All, Length, Any, Required, Coerce

# A subset of sirius.scf's command line options
sirius_options = {
    "control": {
        Optional("processing_unit", default="cpu"): Any("cpu", "gpu"),
        Optional("fft_mode", default="serial"): Any("serial", "parallel"),
        Optional("rmt_max", default=2.2): Coerce(float),
        Optional("verbosity", default=1): Any(0, 1, 2),
        Optional("num_band_to_print", default=10): int,
        Optional("memory_usage", default="high"): Any("low", "medium", "high"),
        Optional("std_evp_solver_type", default="lapack"): Any("lapack", "elpa", "scalapack", "magma"),
        Optional("gen_evp_solver_type", default="lapack"): Any("lapack", "elpa", "scalapack", "magma")
    },
    "parameters": {
        Optional("electronic_structure_method", default="pseudopotential"): Any(
            "pseudopotential", "full_potential_lapwlo"
        ),
        # TODO: add list of valid functionals
        Optional("xc_functionals"): All([str], Length(min=1, max=30)),
        Optional("vwd_functional"): All([str], Length(min=1, max=30)),
        Optional("core_relativity", default="dirac"): Any("dirac", "none"),
        Optional("valence_relativity", default="zora"): Any("zora", "none"),
        Optional("num_fv_states", default=-1): int,
        Optional("smearing_width", default=0.01): Any(float, int),
        Optional("pw_cutoff", default=20): Coerce(float),
        Optional("gk_cutoff", default=6): Coerce(float),
        Optional("num_mag_dims", default=0): Any(0, 1),
        Optional("ngridk"): All([int], Length(min=3, max=3)),
        Optional("vk"): All([All([Any(float, int)], Length(min=3, max=3))]),
        Optional("shiftk"): All([Any(float, int)], Length(min=3, max=3)),
        Optional("num_dft_iter", default=100): int,
        Optional("energy_tol", default=1e-5): Coerce(float),
        Optional("potential_tol", default=1e-5): Coerce(float),
        Optional("molecule", default=False): bool,
        Optional("spin_orbit", default=False): bool,
        Optional("use_symmetry", default=False): bool,
        Optional("hubbard_correction", default=False): bool,
    },
    "mixer": {
        Optional("type", default="broyden1"): Any("linear", "broyden1", "broyden2"),
        Optional("max_history", default=8): int,
        Optional("subspace_size", default=4): int,
        Optional("beta", default=0.7): Coerce(float),
    },
    "unit_cell" : {
        Required("lattice_vectors"): All([All([Coerce(float)], Length(min=3, max=3))],
                                          Length(min=3, max=3)),
        Optional("lattice_vectors_scale"): Any(float, int),
        Required("atom_types"): All([str]),
        Required("atom_files") : All({str: str}),
        Optional("atom_coordinate_units"): Any('au', 'A'),
        Required("atoms"): Any({str: [Any(All([Any(float, int)], Length(min=3, max=3)),
                                          All([Any(float, int)], Length(min=6, max=6)))]})
    },
    "iterative_solver": {
        Optional("type", default="davidson"): Any("davidson", "exact"),
        Optional("num_steps", default=10): int,
        Optional("subspace_size", default=4): int,
        Optional("energy_tolerance", default=0.01): Coerce(float),
        Optional("residual_tolerance", default=1e-6): Coerce(float),
        Optional("empty_state_tolerance", default=1e-6): Coerce(float),
        Optional("orthogonalize", default=True): bool,
        Optional("init_subspace", default="lcao"): Any("lcao", "random"),
        Optional("min_occupancy"): Any(float, int),
        Optional("converge_by_energy", default=0): Any(0, 1),
    },
}
