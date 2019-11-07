# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
## Imports
import os
import mne
from mayavi import mlab
import locale
from pprint import pprint
import numpy as np
import matplotlib.pyplot as plt


# %%
## Parameters

# FreeSurfer path
freesurfer_path = os.path.join('/nfs/diskstation/zccdata/freesurfer')
spacing = 'oct6'  # 4098 sources per hemisphere

# Subject path
subject = 'Subject_02'  # This subject name should consistance with FreeSurfer
raw_path = os.path.join('/nfs/diskstation/zccdata/RSVP_data/rawdata/20190326_RSVP_MEG_maxuelin/S02_lixiangTHU_20190326_05.ds')
epochs_path = os.path.join('/nfs/diskstation/zccdata/RSVP_data/epochs_freq_1.0_50.0/MEG_S02_R%02d/raw-epo.fif')

names = dict(
    fname_aseg   = os.path.join(freesurfer_path, 'subject', subject, 'mri', 'aseg.mgz'),
    fname_src    = os.path.join('%s-%s-src.fif' % (subject, spacing)),
    fname_model  = os.path.join('%s-5120-5120-5120-bem.fif' % subject),
    fname_bem    = os.path.join('%s-5120-5120-5120-bem-sol.fif' % subject),
    fname_raw    = raw_path,
    fname_epochs = epochs_path,
    fname_trans  = os.path.join('%s-trans.fif' % subject),
)

# Bands
band = (0, 4, 'Delta')

pprint(names)


# %%
## Load surfaces files

# Load bem
fname = names['fname_model']
if os.path.exists(fname):
    model = mne.read_bem_surfaces(fname)
else:
    model = mne.make_bem_model(subject)
    mne.write_bem_surfaces(fname, model)
# print(model)

# Load surface sources
fname = names['fname_src']
if os.path.exists(fname):
    src = mne.read_source_spaces(fname)
else:
    src = mne.setup_source_space(subject, spacing=spacing)
    mne.write_source_spaces(fname, src)
# print(src)

# Load bem solutions
fname = names['fname_bem']
if os.path.exists(fname):
    bem_sol = mne.read_bem_solution(fname)
else:
    bem_sol = mne.make_bem_solution(model)
    mne.write_bem_solution(fname, bem_sol)
# print(bem_sol)


# %%
## Load raw and epochs, and compute foward solution

# load raw
locale.setlocale(locale.LC_ALL, "en_US.UTF-8")  # Used by load raw_ctf
raw = mne.io.read_raw_ctf(raw_path, preload=False, verbose=False)
# print(raw.info)

# Load epochs
epochs_list = []
for run in [5]:
    epo = mne.read_epochs(epochs_path % run, verbose=False)
    if epochs_list:
        epo.info['dev_head_t'] = epochs_list[0].info['dev_head_t']
    epochs_list.append(epo)
epochs = mne.epochs.concatenate_epochs(epochs_list)
epochs = epochs.filter(l_freq=band[0], h_freq=band[1], n_jobs=32, verbose=True)
# epochs = mne.read_epochs(epochs_path, verbose=False)
# print(epochs.info)

xdawn = mne.preprocessing.Xdawn(n_components=6, reg='diagonal_fixed')
xdawn.fit(epochs)
epochs = xdawn.apply(epochs.copy(), event_id=['odd'])['odd']

# Load trans
trans = mne.read_trans(names['fname_trans'])
# print(trans)

# Compute forward solution
fwd = mne.make_forward_solution(raw.info, trans, src, bem_sol)


# %%
epochs


# %%
## Compute covariance
noise_cov = mne.compute_covariance(epochs, method='empirical')

## Compute inverse solution and for each epoch

# Parameters
snr = 1.0           # use smaller SNR for raw data
inv_method = 'dSPM'
parc = 'aparc'      # the parcellation to use, e.g., 'aparc' 'aparc.a2009s'
lambda2 = 1.0 / snr ** 2
# Compute inverse operator

inverse_operator = mne.minimum_norm.make_inverse_operator(epochs.info, fwd, noise_cov, depth=None, fixed=False)


# %%
## Compute connectivity
task = 'odd'

# Get labels for FreeSurfer 'aparc' cortical parcellation with 34 labels/hemi
labels_parc = mne.read_labels_from_annot(subject, parc=parc)

# Compute stc
# stc: list of (SourceEstimate | VectorSourceEstimate | VolSourceEstimate)
#      The source estimates for all epochs.
stcs = mne.minimum_norm.apply_inverse_epochs(epochs[task], inverse_operator, lambda2, inv_method,
                            pick_ori=None, return_generator=True)

# Get labels for FreeSurfer 'aparc' cortical parcellation with 34 labels/hemi
labels_parc = mne.read_labels_from_annot(subject, parc=parc)

# Average the source estimates within each label of the cortical parcellation
# and each sub structures contained in the src space
# If mode = 'mean_flip' this option is used only for the cortical label
src = inverse_operator['src']
label_ts = mne.extract_label_time_course(
    stcs, labels_parc, src, mode='mean_flip', allow_empty=True,
    return_generator=True)

# We compute the connectivity in the alpha band and plot it using a circular
# graph layout
fmin = band[0]
fmax = band[1]
sfreq = epochs.info['sfreq']  # the sampling frequency
con, freqs, times, n_epochs, n_tapers = mne.connectivity.spectral_connectivity(
    label_ts, method='pli', mode='multitaper', sfreq=sfreq, fmin=fmin,
    fmax=fmax, faverage=True, mt_adaptive=True, n_jobs=32)

## Plot

# We create a list of Label containing also the sub structures
subjects_dir = os.path.join(freesurfer_path, 'subjects')
labels_aseg = mne.get_volume_labels_from_src(src, subject, subjects_dir)
labels = labels_parc + labels_aseg

# read colors
node_colors = [label.color for label in labels]

# We reorder the labels based on their location in the left hemi
label_names = [label.name for label in labels]
lh_labels = [name for name in label_names if name.endswith('lh')]
rh_labels = [name for name in label_names if name.endswith('rh')]

# Get the y-location of the label
label_ypos_lh = list()
for name in lh_labels:
    idx = label_names.index(name)
    ypos = np.mean(labels[idx].pos[:, 1])
    label_ypos_lh.append(ypos)
try:
    idx = label_names.index('Brain-Stem')
except ValueError:
    pass
else:
    ypos = np.mean(labels[idx].pos[:, 1])
    lh_labels.append('Brain-Stem')
    label_ypos_lh.append(ypos)

# Reorder the labels based on their location
lh_labels = [label for (yp, label) in sorted(zip(label_ypos_lh, lh_labels))]

# For the right hemi
rh_labels = [label[:-2] + 'rh' for label in lh_labels
             if label != 'Brain-Stem' and label[:-2] + 'rh' in rh_labels]

# Save the plot order
node_order = lh_labels[::-1] + rh_labels
node_angles = mne.viz.circular_layout(label_names, node_order, start_pos=90,
                                      group_boundaries=[0, len(label_names) // 2])

# Plot the graph using node colors from the FreeSurfer parcellation. We only
# show the 300 strongest connections.
conmat = con[:, :, 0]
fig = plt.figure(num=None, figsize=(20, 20), facecolor='black')
mne.viz.plot_connectivity_circle(conmat, label_names, n_lines=300,
                                 node_angles=node_angles, node_colors=node_colors,
                                 fontsize_names=16,
                                 vmin=.20,
                                 title='All-to-All Connectivity %s' % task,
                                 fig=fig)
# Plot
plt.show()


# %%



# %%
## Compute connectivity
task = 'clear_norm'

# Get labels for FreeSurfer 'aparc' cortical parcellation with 34 labels/hemi
labels_parc = mne.read_labels_from_annot(subject, parc=parc)

# Compute stc
# stc: list of (SourceEstimate | VectorSourceEstimate | VolSourceEstimate)
#      The source estimates for all epochs.
stcs = mne.minimum_norm.apply_inverse_epochs(epochs[task], inverse_operator, lambda2, inv_method,
                            pick_ori=None, return_generator=True)

# Get labels for FreeSurfer 'aparc' cortical parcellation with 34 labels/hemi
labels_parc = mne.read_labels_from_annot(subject, parc=parc)

# Average the source estimates within each label of the cortical parcellation
# and each sub structures contained in the src space
# If mode = 'mean_flip' this option is used only for the cortical label
src = inverse_operator['src']
label_ts = mne.extract_label_time_course(
    stcs, labels_parc, src, mode='mean_flip', allow_empty=True,
    return_generator=True)

# We compute the connectivity in the alpha band and plot it using a circular
# graph layout
fmin = band[0]
fmax = band[1]
sfreq = epochs.info['sfreq']  # the sampling frequency
con, freqs, times, n_epochs, n_tapers = mne.connectivity.spectral_connectivity(
    label_ts, method='pli', mode='multitaper', sfreq=sfreq, fmin=fmin,
    fmax=fmax, faverage=True, mt_adaptive=True, n_jobs=32)

## Plot

# We create a list of Label containing also the sub structures
subjects_dir = os.path.join(freesurfer_path, 'subjects')
labels_aseg = mne.get_volume_labels_from_src(src, subject, subjects_dir)
labels = labels_parc + labels_aseg

# read colors
node_colors = [label.color for label in labels]

# We reorder the labels based on their location in the left hemi
label_names = [label.name for label in labels]
lh_labels = [name for name in label_names if name.endswith('lh')]
rh_labels = [name for name in label_names if name.endswith('rh')]

# Get the y-location of the label
label_ypos_lh = list()
for name in lh_labels:
    idx = label_names.index(name)
    ypos = np.mean(labels[idx].pos[:, 1])
    label_ypos_lh.append(ypos)
try:
    idx = label_names.index('Brain-Stem')
except ValueError:
    pass
else:
    ypos = np.mean(labels[idx].pos[:, 1])
    lh_labels.append('Brain-Stem')
    label_ypos_lh.append(ypos)

# Reorder the labels based on their location
lh_labels = [label for (yp, label) in sorted(zip(label_ypos_lh, lh_labels))]

# For the right hemi
rh_labels = [label[:-2] + 'rh' for label in lh_labels
             if label != 'Brain-Stem' and label[:-2] + 'rh' in rh_labels]

# Save the plot order
node_order = lh_labels[::-1] + rh_labels
node_angles = mne.viz.circular_layout(label_names, node_order, start_pos=90,
                                      group_boundaries=[0, len(label_names) // 2])

# Plot the graph using node colors from the FreeSurfer parcellation. We only
# show the 300 strongest connections.
conmat = con[:, :, 0]
fig = plt.figure(num=None, figsize=(20, 20), facecolor='black')
mne.viz.plot_connectivity_circle(conmat, label_names, n_lines=300,
                                 node_angles=node_angles, node_colors=node_colors,
                                 fontsize_names=16,
                                 vmin=.20,
                                 title='All-to-All Connectivity %s' % task,
                                 fig=fig)
# Plot
plt.show()


# %%
epochs_saved = epochs.copy()
epochs_saved
help(epochs_saved.crop)


# %%
## Compute connectivity
task = 'odd'

# Get labels for FreeSurfer 'aparc' cortical parcellation with 34 labels/hemi
labels_parc = mne.read_labels_from_annot(subject, parc=parc)

# Compute stc
# stc: list of (SourceEstimate | VectorSourceEstimate | VolSourceEstimate)
#      The source estimates for all epochs.
epochs = epochs_saved.copy()
epochs.crop(tmin=.3, tmax=.6)
stcs = mne.minimum_norm.apply_inverse_epochs(epochs[task], inverse_operator, lambda2, inv_method,
                            pick_ori=None, return_generator=True)

# Get labels for FreeSurfer 'aparc' cortical parcellation with 34 labels/hemi
labels_parc = mne.read_labels_from_annot(subject, parc=parc)

# Average the source estimates within each label of the cortical parcellation
# and each sub structures contained in the src space
# If mode = 'mean_flip' this option is used only for the cortical label
src = inverse_operator['src']
label_ts = mne.extract_label_time_course(
    stcs, labels_parc, src, mode='mean_flip', allow_empty=True,
    return_generator=True)

# We compute the connectivity in the alpha band and plot it using a circular
# graph layout
fmin = band[0]
fmax = band[1]
sfreq = epochs.info['sfreq']  # the sampling frequency
con, freqs, times, n_epochs, n_tapers = mne.connectivity.spectral_connectivity(
    label_ts, method='pli', mode='multitaper', sfreq=sfreq, fmin=fmin,
    fmax=fmax, faverage=True, mt_adaptive=True, n_jobs=32)

## Plot

# We create a list of Label containing also the sub structures
subjects_dir = os.path.join(freesurfer_path, 'subjects')
labels_aseg = mne.get_volume_labels_from_src(src, subject, subjects_dir)
labels = labels_parc + labels_aseg

# read colors
node_colors = [label.color for label in labels]

# We reorder the labels based on their location in the left hemi
label_names = [label.name for label in labels]
lh_labels = [name for name in label_names if name.endswith('lh')]
rh_labels = [name for name in label_names if name.endswith('rh')]

# Get the y-location of the label
label_ypos_lh = list()
for name in lh_labels:
    idx = label_names.index(name)
    ypos = np.mean(labels[idx].pos[:, 1])
    label_ypos_lh.append(ypos)
try:
    idx = label_names.index('Brain-Stem')
except ValueError:
    pass
else:
    ypos = np.mean(labels[idx].pos[:, 1])
    lh_labels.append('Brain-Stem')
    label_ypos_lh.append(ypos)

# Reorder the labels based on their location
lh_labels = [label for (yp, label) in sorted(zip(label_ypos_lh, lh_labels))]

# For the right hemi
rh_labels = [label[:-2] + 'rh' for label in lh_labels
             if label != 'Brain-Stem' and label[:-2] + 'rh' in rh_labels]

# Save the plot order
node_order = lh_labels[::-1] + rh_labels
node_angles = mne.viz.circular_layout(label_names, node_order, start_pos=90,
                                      group_boundaries=[0, len(label_names) // 2])

# Plot the graph using node colors from the FreeSurfer parcellation. We only
# show the 300 strongest connections.
conmat = con[:, :, 0]
fig = plt.figure(num=None, figsize=(20, 20), facecolor='black')
mne.viz.plot_connectivity_circle(conmat, label_names, n_lines=300,
                                 node_angles=node_angles, node_colors=node_colors,
                                 fontsize_names=16,
                                 vmin=.20,
                                 title='All-to-All Connectivity %s' % task,
                                 fig=fig)
# Plot
plt.show()


# %%


