#!/usr/bin/env python3
# coding: utf-8


import numpy as np
import os
import mne
import time
import matplotlib.pyplot as plt

rawfile_path = os.path.join('d:\\RSVP_MEG_experiment\\rawdata',
                            '20190326_RSVP_MEG_maxuelin',
                            'S02_lixiangTHU_20190326_04.ds')

freq_l, freq_h = 1, 30
fir_design = 'firwin'
stim_channel = 'UPPT001'
tmin, tmax = -0.2, 0.8
reject = dict(mag=4e-12)

raw = mne.io.read_raw_ctf(rawfile_path, preload=True)
picks_all_meg = mne.pick_types(raw.info, meg=True, ref_meg=False)

raw.filter(freq_l, freq_h, fir_design=fir_design)

events = mne.find_events(raw, stim_channel=stim_channel)
epochs = mne.Epochs(raw, events, event_id=None, tmin=tmin, tmax=tmax)

ica = mne.preprocessing.ICA(n_components=0.95, method='fastica').fit(
    epochs, picks=picks_all_meg)

ecg_epochs = mne.preprocessing.create_ecg_epochs(raw, tmin=-0.5, tmax=0.5)
ecg_inds, scores = ica.find_bads_ecg(ecg_epochs)

ica.plot_components(show=False)
ica.plot_properties(raw, picks=[0, 1, 2], show=False)

plt.show()
