#!/usr/bin/env python3
"""Artistools - spectra related functions."""

from artistools.nonthermal.nonthermal import (
    Psecondary,
    analyse_ntspectrum,
    ar_xs,
    calculate_Latom_excitation,
    calculate_Latom_ionisation,
    calculate_N_e,
    calculate_frac_heating,
    calculate_nt_frac_excitation,
    differentialsfmatrix_add_ionization_shell,
    e_s_test,
    get_J,
    get_Latom_axelrod,
    get_Lelec_axelrod,
    get_Zbar,
    get_Zboundbar,
    get_arxs_array_ion,
    get_arxs_array_shell,
    get_electronoccupancy,
    get_energyindex_gteq,
    get_energyindex_lteq,
    get_epsilon_avg,
    get_fij_ln_en_ionisation,
    get_lotz_xs_ionisation,
    get_mean_binding_energy,
    get_mean_binding_energy_alt,
    get_nne,
    get_nne_nt,
    get_nnetot,
    get_nntot,
    get_xs_excitation,
    get_xs_excitation_vector,
    lossfunction,
    lossfunction_axelrod,
    namedtuple,
    read_binding_energies,
    read_colliondata,
    sfmatrix_add_excitation,
    sfmatrix_add_ionization_shell,
    solve_spencerfano_differentialform,
    workfunction_tests
)

from artistools.nonthermal.plotnonthermal import main, addargs
