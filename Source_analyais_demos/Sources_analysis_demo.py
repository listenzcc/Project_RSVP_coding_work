# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
# Imports
import os
import mne
from mayavi import mlab
import locale
from pprint import pprint


# %%
# Parameters
subject = 'Subject_02'  # This subject name should consistance with FreeSurfer
spacing = 'oct6'  # 4098 sources per hemisphere
raw_path = os.path.join('/nfs/diskstation/zccdata/RSVP_data/rawdata/20190326_RSVP_MEG_maxuelin/S02_lixiangTHU_20190326_05.ds')
epochs_path = os.path.join('/nfs/diskstation/zccdata/RSVP_data/epochs_freq_1.0_50.0/MEG_S02_R%02d/raw-epo.fif')
trans_path = os.path.join('Subject_02-trans.fif')
freesurfer_path = os.path.join('/nfs/diskstation/zccdata/freesurfer')
names = dict(
    fname_aseg  = os.path.join(freesurfer_path, 'subject', subject, 'mri', 'aseg.mgz'),
    fname_model = os.path.join('%s-5120-5120-5120-bem.fif' % subject),
    fname_bem   = os.path.join('%s-5120-5120-5120-bem_sol.fif' % subject),
    fname_raw   = raw_path,
)

band = (0, 4, 'Delta')

pprint(names)


# %%
# Run `mne coreg` to generate alignment `*-trans.fif` file.
# It is a GUI working requires locations of three fixing points.
# Fixing points' location can be read from `FreeSurfer` GUI.

# Run `mne watershed_bem -s [subject]` before continue.
# To generate surfaces files.


# %%
# Source space
fname = '%s-%s-src.fif' % (subject, spacing)
if os.path.exists(fname):
    src = mne.read_source_spaces(fname)
else:
    src = mne.setup_source_space(subject, spacing=spacing)
    mne.write_source_spaces(fname, src)
print(src)


# %%
# BEM surfaces
fname = '%s-5120-5120-5120-bem.fif' % subject
if os.path.exists(fname):
    model = mne.read_bem_surfaces(fname)
else:
    model = mne.make_bem_model(subject)
    mne.write_bem_surfaces(fname, model)
print(model)
fname_model = fname


# %%
# BEM solution
fname = '%s-5120-5120-5120-bem-sol.fif' % subject
if os.path.exists(fname):
    bem_sol = mne.read_bem_solution(fname)
else:
    bem_sol = mne.make_bem_solution(model)
    mne.write_bem_solution(fname, bem_sol)
print(bem_sol)
fname_bem = fname


# %%
# Read raw and trans; Compute fwd
# Raw, only raw.info is used in below.
# So preload=False is OK and high-efficient.
locale.setlocale(locale.LC_ALL, "en_US.UTF-8")  # Used by load raw_ctf
raw = mne.io.read_raw_ctf(raw_path, preload=False, verbose=False)
print(raw.info)

# Trans
trans = mne.read_trans(trans_path)
print(trans)

# Fwd: forward solution based on raw.info, trans, surfaces and BEM solution.
fwd = mne.make_forward_solution(raw.info, trans, src, bem_sol)


# %%
# Read epochs; Compute cov and inv.

# The order is epochs ==> cov ==> inv.

# Epochs
# Todo: Now is only read single epochs.
#       Awaiting read several epochs and concentrate them.
epochs_list = []
for run in [5, 6, 7, 8]:
    epo = mne.read_epochs(epochs_path % run, verbose=False)
    if epochs_list:
        epo.info['dev_head_t'] = epochs_list[0].info['dev_head_t']
    epochs_list.append(epo)
epochs = mne.epochs.concatenate_epochs(epochs_list)
epochs = epochs.filter(l_freq=band[0], h_freq=band[1], n_jobs=32, verbose=True)
print(epochs.info)

xdawn = mne.preprocessing.Xdawn(n_components=6, reg='diagonal_fixed')
xdawn.fit(epochs)
epochs_xdawn = xdawn.apply(epochs.copy(), event_id=['odd'])['odd']

# Compute cov and inv
# Cov: Covariance using empirical as background noisy.
# Inv: Inverse operator based on fwd and cov.
cov = mne.compute_covariance(epochs, method='empirical')
inv = mne.minimum_norm.make_inverse_operator(raw.info, fwd, cov, loose='auto')

cov_xdawn = mne.compute_covariance(epochs_xdawn, method='empirical')
inv_xdawn = mne.minimum_norm.make_inverse_operator(raw.info, fwd, cov_xdawn, loose='auto')


# %%
# Plot evoked
# evoked: the mean epochs of interest.
# stc: The source estimates.
evoked = epochs_xdawn['clear_norm'].average()
stc, resident = mne.minimum_norm.apply_inverse(evoked, inv, lambda2=0.1, return_residual=True)
print('Evoked')
evoked.plot(spatial_colors=True)
print('Resident')
resident.plot(spatial_colors=True)
print('Done')
# time_viewer=True means stc is plotted in interface manner
stc.plot(time_viewer=True)


# %%
morph = mne.compute_source_morph(stc, subject_from=subject, subject_to='fsaverage')
stc_fsaverage = morph.apply(stc)
stc_fsaverage.plot(time_viewer=True)


# %%


