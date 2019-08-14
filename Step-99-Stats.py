#!/usr/bin/env python3
# coding: utf-8

import mne
import numpy as np
import matplotlib.pyplot as plt

###############################
# Prepare parameters
from mk_stuff_table import stuff_table

# Select subject 02 and meg dataset
stuff = stuff_table['S02_meg']
# User may check the stuff
for e in stuff.items():
    print(e[0], ':', e[1])
p_threshold = 0.05

###############################
# Loop begins
for session_id in stuff['session_range']:
    # For each session, read epochs
    print(session_id)
    if session_id > 4:
        break
    # Read epochs
    epochs = mne.read_epochs(stuff['epochs_path'] % session_id)
    picks = mne.pick_types(epochs.info, meg='mag')

    data = epochs['odd'].get_data()
    times = epochs.times
    times_points = times[::20]
    num = len(times_points)

    p_values_times = np.zeros([len(picks), num])
    for j, t0 in enumerate(times_points):
        print(t0)

        temporal_mask = np.logical_and(t0-0.05 <= times, times <= t0+0.05)
        _data = np.mean(data[:, :, temporal_mask], axis=2)

        n_permutations = 50000
        T0, p_values, H0 = mne.stats.permutation_t_test(_data,
                                                        n_permutations,
                                                        n_jobs=16,
                                                        verbose=2)

        significant_sensors = picks[p_values <= p_threshold]
        significant_sensors_names = [epochs.ch_names[k]
                                     for k in significant_sensors]
        print("Number of significant sensors : %d" % len(significant_sensors))
        print("Sensors names : %s" % significant_sensors_names)

        p_values_times[:, j] = p_values

    mask_times = p_values_times < p_threshold
    info = epochs.info.copy()
    info['sfreq'] = 10
    evoked = mne.EvokedArray(-np.log10(p_values_times),
                             info, tmin=times_points[0])

    evoked.plot_topomap(ch_type='mag', times=times_points, scalings=1,
                        time_format=None, cmap='Reds',
                        vmin=0., vmax=np.max,
                        units='-log10(p)',
                        cbar_fmt='-%0.1f',
                        mask=mask_times,
                        size=3,
                        show_names=False,  # lambda x: x[0:5] + ' ' * 20,
                        time_unit='s')
