#!/usr/bin/env python3
# coding: utf-8


import numpy as np
import os
import mne
import time
import matplotlib.pyplot as plt

''' ==============================================================
Function : Setting parameters
Outputs  : rawfile_path, freq_l, freq_h, fir_design, stim_channel, reject
-------------------------------------------------------------- '''
print('#:', time.ctime(), 'Setting parameters starts.')

rawfile_path = os.path.join('d:\\RSVP_MEG_experiment\\rawdata',
                            '20190326_RSVP_MEG_maxuelin',
                            'S02_lixiangTHU_20190326_04.ds')

freq_l, freq_h = 1, 30
fir_design = 'firwin'
stim_channel = 'UPPT001'
tmin, tmax = -0.2, 0.8
reject = dict(mag=4e-12)
raw = mne.io.read_raw_ctf(rawfile_path)
events = mne.find_events(raw, stim_channel=stim_channel)
event_id = {'odd': 1, 'Norm': 2}

print('#:', time.ctime(), 'Setting parameters done.')


''' ==============================================================
Function : Loading raw data
Outputs  : raw
-------------------------------------------------------------- '''
print('#:', time.ctime(), 'Loading raw data starts.')

raw.load_data()
raw.filter(freq_l, freq_h, fir_design=fir_design)

print('#:', time.ctime(), 'Loading raw data done.')


''' ==============================================================
Function : Calculating ecg_projs
Outputs  : ecg_projs
-------------------------------------------------------------- '''
print('#:', time.ctime(), 'Calculating ecg_projs starts.')

projs, events = mne.preprocessing.compute_proj_ecg(raw, average=True)
print(projs)

ecg_projs = projs
mne.viz.plot_projs_topomap(
    ecg_projs, layout=mne.find_layout(raw.info), show=False)

raw.info['projs'] += ecg_projs

print('#:', time.ctime(), 'Calculating ecg_projs done.')


''' ==============================================================
Function : Computing epochs
Outputs  : epochs_no_proj, epochs_proj
-------------------------------------------------------------- '''
print('#:', time.ctime(), 'Computing epochs starts.')


epochs_no_proj = mne.Epochs(raw, events, event_id, tmin=tmin, tmax=tmax,
                            proj=False, reject=reject)

epochs_proj = mne.Epochs(raw, events, event_id, tmin=tmin, tmax=tmax,
                         proj=True, reject=reject)

epochs_no_proj['odd'].average().plot(
    spatial_colors=True, time_unit='s', show=False)
epochs_proj['odd'].average().plot(
    spatial_colors=True, time_unit='s', show=False)

print('#:', time.ctime(), 'Computing epochs done.')


''' ==============================================================
Function : Interactive proj
Outputs  : None
-------------------------------------------------------------- '''
print('#:', time.ctime(), 'Interactive proj starts.')
epoch_delay_proj = mne.Epochs(raw, events, event_id, tmin=tmin, tmax=tmax,
                              proj='delayed', reject=reject)
evoked = epoch_delay_proj['odd'].average()

# set time instants in seconds (from 50 to 150ms in a step of 10ms)
times = np.arange(tmin, tmax, 0.1)

evoked.plot_topomap(times, proj='interactive', time_unit='s')

print('#:', time.ctime(), 'Interactive proj done.')


plt.show()
