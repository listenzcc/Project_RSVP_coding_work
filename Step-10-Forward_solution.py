#!/usr/bin/env python3
# coding: utf-8
# This is for linux to use freesurfer

import mne
import sys
import os
from mayavi import mlab
from mk_stuff_table import stuff_table

######################
# Init parameters
# Session id
session_id = 7
# Read stuff
stuff = stuff_table['MEG_S02']
rawfile_path = stuff['rawfile_path'] % session_id
rawfile_path = '/mnt/d/' + rawfile_path[4:]
epochs_path = stuff['epochs_path'] % session_id
epochs_path = '/mnt/d/' + epochs_path[4:]
# freesurfer subject
subject = 's02_for_mne'
trans_path = '/mnt/d/freesurfer/subjects/s02_for_mne/s02_coreg-trans.fif'
# Event id
event_id = {'odd': 1, 'norm': 2, 'button': 3, 'clear_norm': 4}
# The directory we store forward solution files
forward_solution_dir = 'dir_forward_solution'
# forward_solution_dir should exists
if not os.path.exists(forward_solution_dir):
    os.mkdir(forward_solution_dir)


def mk_file_path(fname, path=forward_solution_dir, subject=subject):
    # Make file path for forawrd solution files
    fpath = os.path.join(os.path.curdir, path, '%s-%s' % (subject, fname))
    print(fpath)
    return fpath


# Read raw, epochs and trans from file
raw = mne.io.read_raw_ctf(rawfile_path, preload=False)  # only need raw.info
epochs = mne.read_epochs(epochs_path)
trans = mne.read_trans(trans_path)

###############################
# Pipeline for forward solution
# Setup source space
fpath = mk_file_path('oct6-src.fif')
if os.path.exists(fpath):
    src = mne.read_source_spaces(fpath)
else:
    src = mne.setup_source_space(subject, spacing='oct6')
    mne.write_source_spaces(fpath, src)
print(src)

# Make bem model
# bem: boundary-element model (BEM)
fpath = mk_file_path('5120-5120-5120-bem.fif')
if os.path.exists(fpath):
    model = mne.read_bem_surfaces(fpath)
else:
    model = mne.make_bem_model(subject)
    mne.write_bem_surfaces(fpath, model)
print(model)

# Make bem solution
fpath = mk_file_path('5120-5120-5120-bem-sol.fif')
if os.path.exists(fpath):
    bem_sol = mne.read_bem_solution(fpath)
else:
    bem_sol = mne.make_bem_solution(model)
    mne.write_bem_solution(fpath, bem_sol)
print(bem_sol)

# Here we go
fwd = mne.make_forward_solution(raw.info, trans, src, bem_sol, eeg=False)
cov = mne.compute_covariance(epochs, method='empirical')
inv = mne.minimum_norm.make_inverse_operator(raw.info, fwd, cov, loose=0.2)

evoked = epochs['odd'].average()
stc = mne.minimum_norm.apply_inverse(evoked, inv, lambda2=1. / 9.)
stc.plot(time_viewer=True)
