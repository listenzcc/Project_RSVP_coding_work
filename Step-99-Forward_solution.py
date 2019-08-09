#!/usr/bin/env python3
# coding: utf-8
# This is for linux to use freesurfer

import mne
import sys
import os
from mayavi import mlab

###############################
# subject name for freesurfer should exists
subject = 's01_for_mne'
print(subject)

dirname = 'dir_forward_solution'
if not os.path.exists(dirname):
    os.mkdir(dirname)


def mkname(fix, path=dirname, subject=subject):
    return os.path.join(os.path.curdir, path, '%s-%s' % (subject, fix))


###############################
root = 'd:\\'
root = '/mnt/d'
name_table = dict()

name_table['s01_for_mne'] = dict(
    raw='RSVP_MEG_experiment/rawdata/20190326_RSVP_MEG_zhangchuncheng/S01_lixiangTHU_20190326_04.ds',
    epochs='RSVP_MEG_experiment/epochs_saver/epochs_freq_1.0_50.0/MEG_S01_R04/sfreq200_cropn0.2p1.0-epo.fif',
    trans='freesurfer/subjects/s01_for_mne/s01_coreg-trans.fif',
)

name_table['s02_for_mne'] = dict(
    raw='RSVP_MEG_experiment/rawdata/20190326_RSVP_MEG_maxuelin/S02_lixiangTHU_20190326_04.ds',
    epochs='RSVP_MEG_experiment/epochs_saver/epochs_freq_1.0_50.0/MEG_S02_R04/sfreq200_cropn0.2p1.0-epo.fif',
    trans='freesurfer/subjects/s02_for_mne/s02_coreg-trans.fif',
)

print(name_table)


###############################
# pipeline for forward solution
# setup source space
fname = mkname('oct6-src.fif')
if os.path.exists(fname):
    src = mne.read_source_spaces(fname)
else:
    src = mne.setup_source_space(subject, spacing='oct6')
    mne.write_source_spaces(fname, src)
print(src)


# make bem model
# bem: boundary-element model (BEM)
fname = mkname('5120-5120-5120-bem.fif')
if os.path.exists(fname):
    model = mne.read_bem_surfaces(fname)
else:
    model = mne.make_bem_model(subject)
    mne.write_bem_surfaces(fname, model)
print(model)


# make bem solution
fname = mkname('5120-5120-5120-bem-sol.fif')
if os.path.exists(fname):
    bem_sol = mne.read_bem_solution(fname)
else:
    bem_sol = mne.make_bem_solution(model)
    mne.write_bem_solution(fname, bem_sol)
print(bem_sol)


# make forward solution
raw = mne.io.read_raw_ctf(os.path.join(root, name_table[subject]['raw']))
epochs = mne.read_epochs(os.path.join(root, name_table[subject]['epochs']))
fname_trans = os.path.join(root, name_table[subject]['trans'])
trans = mne.read_trans(fname_trans)

# mne.viz.plot_alignment(epochs.info, trans=trans, subject=subject,
#                        src=src, surfaces=['head', 'white'], coord_frame='meg')
# mlab.show()

fwd = mne.make_forward_solution(raw.info, trans, src, bem_sol, eeg=False)

cov = mne.compute_covariance(epochs, method='auto')

inv = mne.minimum_norm.make_inverse_operator(raw.info, fwd, cov, loose=0.2)

evoked = epochs['odd'].average()
stc = mne.minimum_norm.apply_inverse(evoked, inv, lambda2=1. / 9.)
stc.plot()
