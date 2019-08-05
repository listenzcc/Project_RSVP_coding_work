# coding: utf-8

import numpy as np
import os
import mne
import matplotlib.pyplot as plt

from mk_stuff_table import stuff_table

tmin, tmax = -0.2, 1.0
print(stuff_table)

stuff = stuff_table['S02_meg']

epochs_list = []
epochs_denoised_list = []

for session_id in stuff['session_range']:
    print(session_id)
    if session_id > 5:
        continue

    _epochs = mne.read_epochs(stuff['epochs_path'] % session_id)
    if len(epochs_list) > 0:
        _epochs.info['dev_head_t'] = epochs_list[0].info['dev_head_t']

    _cov = mne.read_cov(stuff['cov_path'] % session_id)

    xd = mne.preprocessing.Xdawn(n_components=2, signal_cov=_cov)
    xd.fit(_epochs)
    _epochs_denoised = xd.apply(_epochs.copy())

    epochs_list.append(_epochs)
    epochs_denoised_list.append(_epochs_denoised)

epochs = mne.epochs.concatenate_epochs(epochs_list)

evoked_denoised = dict()
for e in ['odd', 'norm', 'button']:
    _epochs = mne.epochs.concatenate_epochs(
        [d[e][e] for d in epochs_denoised_list])
    evoked_denoised[e] = _epochs.average()

evoked = dict(
    odd=epochs['odd'].average(),
    norm=epochs['norm'].average(),
    button=epochs['button'].average(),
)

times = epochs.times[::20]
for e in evoked.keys():
    evoked[e].plot_topomap(times, average=0.05, time_unit='s',
                           title=e, show=False)
    fig = evoked[e].plot(spatial_colors=True, show=False)
    fig.suptitle(e)

    evoked_denoised[e].plot_topomap(times, average=0.05, time_unit='s',
                                    title=e, show=False)
    fig = evoked_denoised[e].plot(spatial_colors=True, show=False)
    fig.suptitle(e)


plt.show()
