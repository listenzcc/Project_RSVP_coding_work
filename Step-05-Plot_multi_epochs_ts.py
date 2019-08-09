# coding: utf-8

import numpy as np
import os
import mne
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

###############################
# Prepare parameters
from mk_stuff_table import stuff_table
tmin, tmax = -0.2, 1.0  # seconds
l_freq, h_freq = None, 7.0  # Hz
compute_cov = False  # Read covariance from each epochs to save lots of time
n_components = 6  # n_components of Xdawn denoising filter
# Regular scale when plotting
vmin, vmax = -250, 250
ylim = dict(mag=[vmin, vmax])
# Select subject 02 and meg dataset
stuff = stuff_table['S02_meg']
# User may check the stuff
for e in stuff.items():
    print(e[0], ':', e[1])

###############################
# Load epochs
epochs_list = []  # Init empty list for epochs
cov_list = []  # Init empty list for covariance
for session_id in stuff['session_range']:
    # For each session, read epochs
    print(session_id)
    # Limit dataset range if not using server
    if session_id > 5:
        continue
    # Read this epochs as _epochs
    _epochs = mne.read_epochs(stuff['epochs_path'] % session_id)
    # Read covariance of this epochs as _cov
    _cov = mne.read_cov(stuff['cov_path'] % session_id)
    # "Align" dev_head_t across sessions
    # This should raise a warning since actually we are not doing anything
    # But it seems to be all right since the dev_head_ts of
    # different sessions are almost the same
    if len(epochs_list) > 0:
        _epochs.info['dev_head_t'] = epochs_list[0].info['dev_head_t']
    # Append _epochs into epochs_list
    epochs_list.append(_epochs)
    # Append _cov into cov_list
    cov_list.append(_cov)

######################
# Concatenate epochs in epochs_list
epochs = mne.epochs.concatenate_epochs(epochs_list)
# Filter epochs, filter function seems not applied in-place
epochs = epochs.filter(l_freq=l_freq, h_freq=h_freq,
                       h_trans_bandwidth=3,
                       n_jobs=16, verbose=2)

######################
# Xdawn preprocessing
# Compute covariance
print('Computing covariance, this can be slow.')
if compute_cov:
    cov = mne.compute_covariance(epochs, method='auto', n_jobs=16, verbose=2)
else:
    print('Using covariance from epochs, which is pre computed.')
    cov_data = np.zeros([len(cov_list), 272, 272])
    for j, cov in enumerate(cov_list):
        cov_data[j, :, :] = cov.data
    cov = mne.make_ad_hoc_cov(epochs.info)
    cov['data'] = cov_data.mean(0)
print('Done.')
# Init and fit Xdawn filter
xd = mne.preprocessing.Xdawn(n_components=n_components, signal_cov=cov)
print('Xdawn fitting, this can be slow.')
xd.fit(epochs)
print('Done.')

######################
# Xdawn filter denoise
evoked_denoised = dict()
# Apply Xdawn filter
print('Xdawn applying, this can be slow.')
epochs_denoised = xd.apply(epochs.copy())
epochs_denoised = epochs_denoised['odd']
print('Done.')

###############################
# Compute evoked from raw epochs and denoised epochs
# Raw
evoked = dict(
    odd=epochs['odd'].average(),
    norm=epochs['norm'].average(),
    button=epochs['button'].average(),
)
# Denoised
evoked_denoised = dict(
    odd=epochs_denoised['odd'].average(),
    norm=epochs_denoised['norm'].average(),
    button=epochs_denoised['button'].average(),
)

######################
# Plot results
times = epochs.times[::20].reshape(2, 6)

for e in evoked.keys():
    fig, axes = plt.subplots(2, 6)
    for t, a in zip(times, axes):
        evoked[e].plot_topomap(times=t, axes=a, average=0.05,
                               vmin=vmin, vmax=vmax,
                               time_unit='s',
                               colorbar=False, show=False)
    fig.suptitle(e)
    fig = evoked[e].plot(spatial_colors=True, show=False)
    fig.suptitle(e)

    fig, axes = plt.subplots(2, 6)
    for t, a in zip(times, axes):
        evoked_denoised[e].plot_topomap(times=t, axes=a, average=0.05,
                                        vmin=vmin, vmax=vmax,
                                        time_unit='s',
                                        colorbar=False, show=False)
    fig.suptitle(e+'_denoised')
    fig = evoked_denoised[e].plot(spatial_colors=True, show=False)
    fig.suptitle(e+'_denoised')


plt.show()
