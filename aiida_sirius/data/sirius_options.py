from voluptuous import Optional, Schema, All, Length, Any

# A subset of sirius.scf's command line options
sirius_options = {
    "control": {
        Optional("processing_unit", default="CPU"): Any("CPU", "GPU"),
        Optional("fft_mode", default="serial"): Any("serial", "parallel"),
        Optional("rmt_max", default=2.2): float,
        Optional("verbosity", default=1): Any(0, 1, 2),
        Optional("num_band_to_print", default=10): int,
        Optional("memory_usage", default="high"): Any("low", "medium", "high"),
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
        Optional("smearing_width", default=0.01): float,
        Optional("pw_cutoff", default=20): float,
        Optional("gk_cutoff", default=6): float,
        Optional("num_mag_dims", default=0): Any(0, 1),
        Optional("ngridk", default=[1, 1, 1]): All([int], Length(min=3, max=3)),
        Optional("shiftk", default=[0, 0, 0]): All([int], Length(min=3, max=3)),
        Optional("num_dft_iter", default=100): int,
        Optional("energy_tol", default=1e-5): float,
        Optional("potential_tol", default=1e-5): float,
        Optional("molecule", default=False): bool,
        Optional("spin_orbit", default=False): bool,
        Optional("use_symmetry", default=False): bool,
        Optional("hubbard_correction", default=False): bool,
    },
    "mixer": {
        Optional("type", default="broyden1"): Any("linear", "broyden1", "broyden2"),
        Optional("max_history", default=8): int,
        Optional("subspace_size", default=4): int,
        Optional("beta", default=0.7): float,
    },
    "iterative_solver": {
        Optional("type", default="davidson"): Any("davidson", "exact"),
        Optional("num_steps", default=10): int,
        Optional("subspace_size", default=4): int,
        Optional("energy_tolerance", default=0.01): float,
        Optional("residual_tolerance", default=1e-6): float,
        Optional("empty_state_tolerance", default=1e-6): float,
        Optional("orthogonalize", default=True): bool,
        Optional("init_subspace", default="lcao"): Any("lcao", "random"),
        Optional("converge_by_energy", default=0): Any(0, 1),
    },
}
