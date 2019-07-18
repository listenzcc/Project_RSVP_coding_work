#!/usr/bin/env python3
# coding: utf-8

import os
import mne
import time
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


''' ==============================================================
Function : Setting independence parameters
Outputs  : event_id, freq_l, freq_h, tmin, tmax, fir_design,
           ica, sfreq, figs
-------------------------------------------------------------- '''
print('#:', time.ctime(), 'Setting independence parameters starts.')

event_id = {'odd': 1, 'norm': 2, 'button': 3}
freq_l, freq_h = 1, 50
tmin, tmax = -0.2, 1.0
fir_design = 'firwin'
ica = mne.preprocessing.ICA(n_components=0.95, method='fastica')
sfreq = 200
root = 'd:\\RSVP_MEG_experiment'

print('#:', time.ctime(), 'Setting independence parameters done.')


''' ==============================================================
Function : Generating read_save_stuff
Outputs  : read_save_stuff
-------------------------------------------------------------- '''
print('#:', time.ctime(), 'Generating read_save_stuff starts.')

read_save_stuff = {}

read_save_stuff['S02'] = dict(
    session_range=range(4, 12),
    rawfile_path=os.path.join(root, 'rawdata',
                              '20190326_RSVP_MEG_maxuelin',
                              'S02_lixiangTHU_20190326_%02d.ds'),
    report_path=os.path.join(root, 'epochs_saver',
                             'epochs_freq_1.0_30_crop_n0.2_p1.0',
                             'meg_epoch_S02_%02d.pdf'))

read_save_stuff['S01'] = dict(
    session_range=range(4, 11),
    rawfile_path=os.path.join(root, 'rawdata',
                              '20190326_RSVP_MEG_zhangchuncheng',
                              'S02_lixiangTHU_20190326_%02d.ds'),
    report_path=os.path.join(root, 'epochs_saver',
                             'epochs_freq_1.0_30_crop_n0.2_p1.0',
                             'meg_epoch_S01_%02d.pdf'))

newdir = os.path.join(root, 'epochs_saver',
                      'epochs_freq_1.0_30_crop_n0.2_p1.0')
if not os.path.exists(newdir):
    os.mkdir(newdir)

print('#:', time.ctime(), 'Generating read_save_stuff done.')


''' ==============================================================
Function : For each stuff
-------------------------------------------------------------- '''
for stuff in read_save_stuff.values():
    figs = []

    rawfile_path = stuff['rawfile_path']
    report_path = stuff['report_path']

    for session_id in stuff['session_range']:
        print(rawfile_path % session_id)
        print(report_path % session_id)

        ''' ==============================================================
        Function : Loading rawdata
        Outputs  : None
        -------------------------------------------------------------- '''
        print('#:', time.ctime(), 'Loading rawdata starts.')

        raw = mne.io.read_raw_ctf(rawfile_path % session_id)
        picks = mne.pick_types(raw.info, meg=True, ref_meg=False)
        events = mne.find_events(raw, stim_channel='UPPT001')

        raw.load_data()
        raw.filter(freq_l, freq_h, fir_design=fir_design)
        figs.append(raw.plot_psd(tmax=np.inf, fmax=freq_h, show=False))

        print('#:', time.ctime(), 'Loading rawdata done.')

        ''' ==============================================================
        Function : Computing epochs
        Outputs  : None
        -------------------------------------------------------------- '''
        print('#:', time.ctime(), 'Computing epochs starts.')

        epochs = mne.Epochs(raw, events, event_id=event_id, picks=picks,
                            tmin=tmin, tmax=tmax, detrend=1, preload=True)
        epochs.resample(200)

        print('#:', time.ctime(), 'Computing epochs done.')

        ''' ==============================================================
        Function : Calculating ICA
        Outputs  : ica: fitted ica instance
        -------------------------------------------------------------- '''
        print('#:', time.ctime(), 'Calculating ICA starts.')

        ica.fit(raw, picks=picks)
        [figs.append(f) for f in ica.plot_components(show=False)]

        print('#:', time.ctime(), 'Calculating ICA done.')

        with PdfPages(report_path % session_id) as pp:
            for f in figs:
                pp.savefig(f)

        plt.close('all')
