#!/usr/bin/env python3
"""Artistools.

A collection of plotting, analysis, and file format conversion tools for the ARTIS radiative transfer code.
"""

import sys
from artistools.configuration import config
from artistools.misc import (
    AppendPath,
    CustomArgHelpFormatter,
    cross_prod,
    decode_roman_numeral,
    diskcache,
    dot,
    elsymbols,
    ExponentLabelFormatter,
    firstexisting,
    flatten_list,
    gather_res_data,
    get_artis_constants,
    get_atomic_number,
    get_cellsofmpirank,
    get_composition_data,
    get_composition_data_from_outputfile,
    get_deposition,
    get_elsymbol,
    get_filterfunc,
    get_model_name,
    get_inputparams,
    get_ionstring,
    get_mpiranklist,
    get_mpirankofcell, get_runfolders,
    get_syn_dir, get_time_range,
    get_timestep_of_timedays,
    get_timestep_time,
    get_timestep_times_float,
    get_vpkt_config,
    get_wid_init_at_tmin,
    get_wid_init_at_tmodel,
    get_z_a_nucname,
    join_pdf_files,
    make_namedtuple,
    makelist,
    match_closest_time,
    namedtuple,
    parse_cdefines,
    parse_range,
    parse_range_list,
    readnoncommentline,
    roman_numerals,
    showtimesteptimes,
    stripallsuffixes,
    trim_or_pad,
    vec_len,
    zopen,
)

import artistools.atomic
import artistools.codecomparison
import artistools.deposition
import artistools.estimators
import artistools.inputmodel
import artistools.lightcurve
import artistools.macroatom
import artistools.nltepops
import artistools.nonthermal
import artistools.packets
import artistools.radfield
import artistools.spectra
import artistools.transitions
import artistools.plottools

from artistools.__main__ import main, addargs


if sys.version_info < (3,):
    print("Python 2 not supported")
