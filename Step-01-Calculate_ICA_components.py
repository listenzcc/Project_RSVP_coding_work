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
Outputs  : event_id, freq_l, freq_h, fir_design, ica, sfreq, figs
-------------------------------------------------------------- '''
print('#:', time.ctime(), 'Setting independence parameters starts.')

event_id = {'odd': 1, 'norm': 2, 'button': 3}
freq_l, freq_h = 1, 50
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

newdir = os.path.join(root, 'epochs_saver', 'epochs_freq_1.0_50.0')
# Protect existing results in newdir
assert(not os.path.exists(newdir))
os.mkdir(newdir)

read_save_stuff = {}

read_save_stuff['S01_eeg'] = dict(
    session_range=range(1, 11),
    rawfile_path=os.path.join(root, 'rawdata',
                              '20190402_RSVP_EEG_zhangchuncheng',
                              'zcc%d.cnt'),
    report_dir=os.path.join(newdir, 'EEG_S01_R%02d'))

read_save_stuff['S02_eeg'] = dict(
    session_range=range(1, 11),
    rawfile_path=os.path.join(root, 'rawdata',
                              '20190402_RSVP_EEG_maxuelin',
                              'mxl%d.cnt'),
    report_dir=os.path.join(newdir, 'EEG_S02_R%02d'))

read_save_stuff['S01_meg'] = dict(
    session_range=range(4, 11),
    rawfile_path=os.path.join(root, 'rawdata',
                              '20190326_RSVP_MEG_zhangchuncheng',
                              'S01_lixiangTHU_20190326_%02d.ds'),
    report_dir=os.path.join(newdir, 'MEG_S01_R%02d'))

read_save_stuff['S02_meg'] = dict(
    session_range=range(4, 12),
    rawfile_path=os.path.join(root, 'rawdata',
                              '20190326_RSVP_MEG_maxuelin',
                              'S02_lixiangTHU_20190326_%02d.ds'),
    report_dir=os.path.join(newdir, 'MEG_S02_R%02d'))

print('#:', time.ctime(), 'Generating read_save_stuff done.')


''' ==============================================================
Function : For each stuff
-------------------------------------------------------------- '''
for stuff in read_save_stuff.values():

    for session_id in stuff['session_range']:
        rawfile_path = stuff['rawfile_path'] % session_id
        report_dir = stuff['report_dir'] % session_id

        print(rawfile_path)
        print(report_dir)
        if not os.path.exists(report_dir):
            os.mkdir(report_dir)

        figs = []

        ''' ==============================================================
        Function : Loading rawdata
        Outputs  : None
        -------------------------------------------------------------- '''
        print('#:', time.ctime(), 'Loading rawdata starts.')

        if rawfile_path.endswith('.ds'):
            # if is MEG data
            raw = mne.io.read_raw_ctf(rawfile_path)
            picks = mne.pick_types(raw.info, meg=True, ref_meg=False)
            events = mne.find_events(raw, stim_channel='UPPT001')
        else:
            # if is EEG data
            raw = mne.io.read_raw_cnt(rawfile_path,
                                      mne.channels.read_montage(
                                          'standard_1020'),
                                      stim_channel='STI 014')
            picks = mne.pick_types(raw.info, eeg=True)
            events = mne.find_events(raw)

        raw.load_data()
        raw.filter(freq_l, freq_h, fir_design=fir_design)
        figs.append(raw.plot_psd(tmax=np.inf, fmax=freq_h, show=False))

        print('#:', time.ctime(), 'Loading rawdata done.')

        ''' ==============================================================
        Function : Calculating ICA
        Outputs  : ica: fitted ica instance
        -------------------------------------------------------------- '''
        print('#:', time.ctime(), 'Calculating ICA starts.')

        ica.fit(raw, picks=picks)
        [figs.append(f) for f in ica.plot_components(show=False)]
        [figs.append(f) for f in ica.plot_properties(
            raw, range(ica.n_components_), show=False)]

        print('#:', time.ctime(), 'Calculating ICA done.')

        ''' ==============================================================
        Function : Saving results
        Outputs  : None
        -------------------------------------------------------------- '''
        print('#:', time.ctime(), 'Saving results starts.')

        ica.save(os.path.join(report_dir, 'raw_ica.fif'))

        info = {e[0]: e[1] for e in raw.info.items()}
        with open(os.path.join(report_dir, 'raw_info.txt'), 'w') as f:
            for e in info.items():
                f.write(e[0])
                f.write(': ')
                if e[1] is not None:
                    f.write(str(e[1]))
                f.write('\n')

        with PdfPages(os.path.join(
                report_dir, 'raw_ica_report.pdf')) as pp:
            for f in figs:
                pp.savefig(f)

        print('#:', time.ctime(), 'Saving results done.')

        plt.close('all')
