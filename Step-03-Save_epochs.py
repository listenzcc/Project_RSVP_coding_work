#!/usr/bin/env python3
# coding: utf-8

import json
import os
import mne
import time
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from mk_stuff_table import stuff_table, epochs_root


###############################
# Prepare parameters
event_id = {'odd': 1, 'norm': 2, 'button': 3, 'clear_norm': 4}
freq_l, freq_h = 1, 50
fir_design = 'firwin'
tmin, tmax = -0.2, 1.0
sfreq = 200
# Reading bad_ICA_components table
with open(os.path.join(epochs_root, 'bad_ICA_components.json'), 'r') as f:
    x = f.readlines()
    bad_ICA_components = json.loads(x[0])

print(bad_ICA_components)

###############################
# Select subject 02 and meg dataset
# stuff = stuff_table['MEG_S02']
for stuff in stuff_table.values():
    # User may check the stuff
    for e in stuff.items():
        print(e[0], ':', e[1])

    ###############################
    # For each session
    for session_id in stuff['session_range']:
        rawfile_path = stuff['rawfile_path'] % session_id
        raw_ica_path = stuff['raw_ica_fif_path'] % session_id
        epochs_path = stuff['epochs_path'] % session_id
        print('-' * 60)
        if os.path.exists(epochs_path):
            print(epochs_path, 'exists, pass.')
            continue
        print(rawfile_path)
        print(raw_ica_path)
        print(epochs_path)

        # Read rawfile
        is_legal_data = False
        if rawfile_path.endswith('.ds'):
            # if is MEG data
            raw = mne.io.read_raw_ctf(rawfile_path)
            picks = mne.pick_types(raw.info, meg=True, ref_meg=False)
            events = mne.find_events(raw, stim_channel='UPPT001')
            reject = dict(mag=4e-12)
            is_legal_data = True
        if rawfile_path.endswith('.cnt'):
            # if is EEG data
            raw = mne.io.read_raw_cnt(rawfile_path,
                                      mne.channels.read_montage(
                                          'standard_1020'),
                                      stim_channel='STI 014')
            picks = mne.pick_types(raw.info, eeg=True)
            events = mne.find_events(raw)
            reject = dict()
            is_legal_data = True
        assert(is_legal_data)

        # Load rawfile and filter
        raw.load_data()
        raw.filter(freq_l, freq_h, fir_design=fir_design, verbose=1)

        # Apply ICA
        ica = mne.preprocessing.read_ica(raw_ica_path)
        ica.apply(raw, exclude=bad_ICA_components[
            os.path.basename(os.path.dirname(raw_ica_path))])

        # Re-mark norm events as clear_norm if it not in +-1s range of odd
        # Records ts: time points
        ts = dict()
        for id in event_id.keys():
            print(id)
            ts[id] = [e[0] for e in events if e[2] == event_id[id]]

        # Re-mark
        new_events = events.copy()
        for t in ts['norm']:
            # For every norm events
            if any(abs(t-x) < 1200 for x in ts['odd']):
                # If in +-1s of odd, do not re-mark
                continue
            # Re-mark as 4, since it is clear
            new_events[events[:, 0] == t, 2] = 4

        # Computing epochs
        epochs = mne.Epochs(raw, picks=picks,
                            events=new_events, event_id=event_id,
                            tmin=tmin, tmax=tmax, baseline=None, detrend=1,
                            reject=reject, preload=True)
        epochs.resample(sfreq, verbose=2)

        ###############################
        # Saving epochs
        print('Saving epochs.')
        epochs.save(epochs_path, overwrite=False, verbose=2)
        print('Done.')
