#!/usr/bin/env python3
# coding: utf-8

import numpy as np

import os
import mne
from mne.preprocessing import create_ecg_epochs, create_eog_epochs

# getting some data ready
rawfile_path = os.path.join('d:\\RSVP_MEG_experiment\\rawdata',
                            '20190326_RSVP_MEG_maxuelin',
                            'S02_lixiangTHU_20190326_07.ds')

raw = mne.io.read_raw_ctf(rawfile_path, preload=True)
picks = mne.pick_types(raw.info, meg=True, ref_meg=False)
###############################################################################
# Low frequency drifts and line noise

(raw.copy().pick_types(meg=True)
           .plot(duration=60, n_channels=100, remove_dc=False))

###############################################################################
# we see high amplitude undulations in low frequencies, spanning across tens of
# seconds

raw.plot_psd(tmax=np.inf, fmax=250)

###############################################################################
# On MEG sensors we see narrow frequency peaks at 60, 120, 180, 240 Hz,
# related to line noise.
# But also some high amplitude signals between 25 and 32 Hz, hinting at other
# biological artifacts such as ECG. These can be most easily detected in the
# time domain using MNE helper functions
#
# See :ref:`tut-filter-resample`.

###############################################################################
# ECG
# ---
#
# finds ECG events, creates epochs, averages and plots

average_ecg = create_ecg_epochs(raw, picks=picks).average()
print('We found %i ECG events' % average_ecg.nave)
joint_kwargs = dict(ts_args=dict(time_unit='s'),
                    topomap_args=dict(time_unit='s'))
average_ecg.plot_joint(**joint_kwargs)

###############################################################################
# we can see typical time courses and non dipolar topographies
# not the order of magnitude of the average artifact related signal and
# compare this to what you observe for brain signals

###############################################################################
# EOG
# ---

average_eog = create_eog_epochs(raw).average()
print('We found %i EOG events' % average_eog.nave)
average_eog.plot_joint(**joint_kwargs)

###############################################################################
# Knowing these artifact patterns is of paramount importance when
# judging about the quality of artifact removal techniques such as SSP or ICA.
# As a rule of thumb you need artifact amplitudes orders of magnitude higher
# than your signal of interest and you need a few of such events in order
# to find decompositions that allow you to estimate and remove patterns related
# to artifacts.
#
# Consider the following tutorials for correcting this class of artifacts:
# - :ref:`tut-filter-resample`
# - :ref:`tut-artifact-ica`
# - :ref:`tut-artifact-ssp`
