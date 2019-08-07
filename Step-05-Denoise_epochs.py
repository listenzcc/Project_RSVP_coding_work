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
# Loop begins
for session_id in stuff['session_range']:
    # For each session, read epochs
    print(session_id)
    # Read epochs
    epochs = mne.read_epochs(stuff['epochs_path'] % session_id)
    # Read covariance of the epochs
    cov = mne.read_cov(stuff['cov_path'] % session_id)

    # Filter epochs, filter function seems not applied in-place
    epochs = epochs.filter(l_freq=l_freq, h_freq=h_freq,
                           h_trans_bandwidth=3,
                           n_jobs=1, verbose=2)
    # epochs = epochs.crop(tmin=-0.1, tmax=0.8)

    ######################
    # Xdawn preprocessing
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
    epochs_denoised.save(stuff['denoised_epochs_path'] % session_id)
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

    figs = []
    for e in evoked.keys():
        # Raw plot_topomap
        fig, axes = plt.subplots(2, 6)
        for t, a in zip(times, axes):
            evoked[e].plot_topomap(times=t, axes=a, average=0.05,
                                   vmin=vmin, vmax=vmax,
                                   time_unit='s',
                                   colorbar=False, show=False)
        fig.suptitle(e)
        figs.append(fig)
        # Raw evoked
        fig = evoked[e].plot(spatial_colors=True, ylim=ylim,
                             show=False)
        fig.suptitle(e)
        figs.append(fig)
        # Denoised plot_topomap
        fig, axes = plt.subplots(2, 6)
        for t, a in zip(times, axes):
            evoked_denoised[e].plot_topomap(times=t, axes=a, average=0.05,
                                            vmin=vmin, vmax=vmax,
                                            time_unit='s',
                                            colorbar=False, show=False)
        fig.suptitle(e+'_denoised')
        figs.append(fig)
        # Denoised evoked
        fig = evoked_denoised[e].plot(spatial_colors=True, ylim=ylim,
                                      show=False)
        fig.suptitle(e+'_denoised')
        figs.append(fig)

    # Write figures into pdf report file
    with PdfPages(stuff['epochs_ts_report_path'] % session_id, 'w') as pp:
        for f in figs:
            pp.savefig(f)

    # Clear figures from buffers, they are already in pdf file
    plt.close('all')
