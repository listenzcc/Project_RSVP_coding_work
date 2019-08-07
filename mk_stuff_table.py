#!/usr/bin/env python3
# coding: utf-8

import os

###############################
# Make stuff table for access MEG data

raw_data_root = 'd:\\RSVP_MEG_experiment\\rawdata'
epochs_root = 'd:\\RSVP_MEG_experiment\\epochs_saver'
freesurfer_root = 'd:\\freesurfer\\subjects'

epochs_freq_ = 'epochs_freq_1.0_50.0'

stuff_table = dict()

###############################
# Subject 01
MEG_S01_R_ = 'MEG_S01_R%02d'
stuff_table['S01_meg'] = dict(
    subject_truename='zhangchuncheng',
    subject_id='S01',
    subject_freesurfer='s01_for_mne',
    session_range=range(4, 11),
    rawfile_path=os.path.join(
        raw_data_root,
        '20190326_RSVP_MEG_zhangchuncheng',
        'S01_lixiangTHU_20190326_%02d.ds'
        ),
    epochs_path=os.path.join(
        epochs_root,
        epochs_freq_,
        MEG_S01_R_,
        'sfreq200_cropn0.2p1.0-epo.fif'
        ),
    denoised_epochs_path=os.path.join(
        epochs_root,
        epochs_freq_,
        MEG_S01_R_,
        'sfreq200_cropn0.2p1.0-den_epo.fif'
        ),
    raw_ica_report_path=os.path.join(
        epochs_root,
        epochs_freq_,
        MEG_S01_R_,
        'raw_ica_report.pdf',
        ),
    cov_path=os.path.join(
        epochs_root,
        epochs_freq_,
        MEG_S01_R_,
        'xxx-epo-cov.fif'),
    epochs_ts_report_path=os.path.join(
        epochs_root,
        epochs_freq_,
        MEG_S01_R_,
        'epochs_ts_report.pdf',
        ),
    trans=os.path.join(
        freesurfer_root,
        's01_for_mne/s01_coreg-trans.fif'
        ),
)

###############################
# Subject 02
MEG_S02_R_ = 'MEG_S02_R%02d'
stuff_table['S02_meg'] = dict(
    subject_truename='maxuelin',
    subject_id='S02',
    subject_freesurfer='s02_for_mne',
    session_range=range(4, 11),
    rawfile_path=os.path.join(
        raw_data_root,
        '20190326_RSVP_MEG_maxuelin',
        'S02_lixiangTHU_20190326_%02d.ds'
        ),
    epochs_path=os.path.join(
        epochs_root,
        epochs_freq_,
        MEG_S02_R_,
        'sfreq200_cropn0.2p1.0-epo.fif'
        ),
    denoised_epochs_path=os.path.join(
        epochs_root,
        epochs_freq_,
        MEG_S02_R_,
        'sfreq200_cropn0.2p1.0-den_epo.fif'
        ),
    raw_ica_report_path=os.path.join(
        epochs_root,
        epochs_freq_,
        MEG_S02_R_,
        'raw_ica_report.pdf',
        ),
    cov_path=os.path.join(
        epochs_root,
        epochs_freq_,
        MEG_S02_R_,
        'xxx-epo-cov.fif'
        ),
    epochs_ts_report_path=os.path.join(
        epochs_root,
        epochs_freq_,
        MEG_S02_R_,
        'epochs_ts_report.pdf',
        ),
    trans=os.path.join(
        freesurfer_root,
        's02_for_mne/s02_coreg-trans.fif'
        ),
)

print(stuff_table)