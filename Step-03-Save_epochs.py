import json
import os
import mne
import time
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


''' ==============================================================
Function : Setting independence parameters
Outputs  : event_id, freq_l, freq_h, fir_design, sfreq
-------------------------------------------------------------- '''
print('#:', time.ctime(), 'Setting independence parameters starts.')

event_id = {'odd': 1, 'norm': 2, 'button': 3}
freq_l, freq_h = 1, 50
fir_design = 'firwin'
tmin, tmax = -0.2, 1.0
sfreq = 200
root = 'd:\\RSVP_MEG_experiment'

print('#:', time.ctime(), 'Setting independence parameters done.')


''' ==============================================================
Function : Generating read_save_stuff
Outputs  : read_save_stuff
-------------------------------------------------------------- '''
print('#:', time.ctime(), 'Generating read_save_stuff starts.')

newdir = os.path.join(root, 'epochs_saver', 'epochs_freq_1.0_50.0')
# Assume newdir exists
assert(os.path.exists(newdir))

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


###############################
# Reading bad_ICA_components table
with open(os.path.join(newdir, 'bad_ICA_components.json'), 'r') as f:
  x = f.readlines()
  bad_ICA_components = json.loads(x[0])

print(bad_ICA_components)


''' ==============================================================
Function : For each stuff
-------------------------------------------------------------- '''
for stuff in read_save_stuff.values():

    for session_id in stuff['session_range']:
        rawfile_path = stuff['rawfile_path'] % session_id
        report_dir = stuff['report_dir'] % session_id

        print(rawfile_path)
        print(report_dir)
        assert(os.path.exists(report_dir))

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
            reject = dict(mag=4e-12)
        else:
            # if is EEG data
            raw = mne.io.read_raw_cnt(rawfile_path,
                                      mne.channels.read_montage(
                                          'standard_1020'),
                                      stim_channel='STI 014')
            picks = mne.pick_types(raw.info, eeg=True)
            events = mne.find_events(raw)
            reject = dict()

        raw.load_data()
        raw.filter(freq_l, freq_h, fir_design=fir_design)

        print('#:', time.ctime(), 'Loading rawdata done.')

        ''' ==============================================================
        Function : Read and apply ICA
        Outputs  : ica: fitted ica instance
        -------------------------------------------------------------- '''
        print('#:', time.ctime(), 'Reading ICA starts.')

        ica = mne.preprocessing.read_ica(os.path.join(report_dir, 'raw_ica.fif'))
        ica.apply(raw, exclude=bad_ICA_components[os.path.basename(report_dir)])

        print('#:', time.ctime(), 'Reading ICA done.')


        ###############################
        # Computing epochs
        epochs = mne.Epochs(raw, picks=picks, events=events, event_id=event_id,
                            tmin=tmin, tmax=tmax, baseline=None, detrend=1,
                            reject=reject, preload=True)
        epochs.resample(sfreq)

        ###############################
        # Saving epochs
        epochs.save(os.path.join(report_dir, 'sfreq200_cropn0.2p1.0-epo.fif'))
        print(os.path.basename(report_dir), 'Saving epochs done.')

