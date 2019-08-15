#!/usr/bin/env python3
# coding: utf-8

import os

###############################
# Make stuff table for access MEG data

raw_data_root = os.path.join('d:\\', 'RSVP_MEG_experiment', 'rawdata')
epochs_root = os.path.join(
    'd:\\', 'RSVP_MEG_experiment', 'epochs_saver', 'epochs_freq_1.0_50.0')
freesurfer_root = 'd:\\freesurfer\\subjects'

epochs_freq_ = 'epochs_freq_1.0_50.0'

event_id = {'odd': 1, 'norm': 2, 'button': 3, 'clear_norm': 4}

stuff_table = dict()

for subject_id, rawfile_id, session_range in [
        # MEG Subject 01
        ['MEG_S01',
         os.path.join('20190326_RSVP_MEG_zhangchuncheng',
                      'S01_lixiangTHU_20190326_%02d.ds'),
         range(4, 11)],
        # MEG Subject 02
        ['MEG_S02',
         os.path.join('20190326_RSVP_MEG_maxuelin',
                      'S02_lixiangTHU_20190326_%02d.ds'),
         range(4, 12)],
        # EEG Subject 01
        ['EEG_S01',
        os.path.join('20190402_RSVP_EEG_zhangchuncheng',
                              'zcc%d.cnt'),
        range(1, 11)],
        # EEG Subject 02
        ['EEG_S02',
        os.path.join('20190402_RSVP_EEG_maxuelin',
                              'mxl%d.cnt'),
        range(1, 11)],
]:

    working_path = os.path.join(epochs_root, '%s_R%s' %
                                (subject_id, '%02d'))

    print('\n'.join(['='*80, subject_id, rawfile_id, working_path]))

    stuff_table[subject_id] = {
        # Subject id
        'subject_id': subject_id,

        # Main working path
        'working_path': working_path,

        # The sessions we used
        'session_range': session_range,

        # Original raw file
        'rawfile_path': os.path.join(
            raw_data_root,
            rawfile_id),

        # ICA fif file on raw fif
        'raw_ica_fif_path': os.path.join(
            working_path, 'raw_ica.fif'),

        # ICA report
        'raw_ica_report_path': os.path.join(
            working_path, 'raw_ica_report.pdf'),

        # Epochs from Filtered and ICAed raw file
        'epochs_path': os.path.join(
            working_path, 'raw-epo.fif'),

        # Evoked joints of raw-epo
        'evoked_joint_report_path': os.path.join(
            working_path, 'evoked_joint_report.pdf'),

        # Covariance fif on raw-epo
        'cov_path': os.path.join(
            working_path, 'raw-epo-cov.fif'),

        # Denoised epochs using Xdawn
        'denoised_epochs_path': os.path.join(
            working_path, 'denoised-epo.fif'),

        # Todo
        # Freesurfer path
        # Forward solution path
    }


'''
trans=os.path.join(
        freesurfer_root,
        's02_for_mne/s02_coreg-trans.fif'
    ),
'''
