# coding: utf-8

import os
import sys
import numpy as np

import mne
from mne.decoding import SlidingEstimator

import pickle

from sklearn import svm
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import LeaveOneGroupOut

from mk_stuff_table import stuff_table

bands = [(0, 4, 'Delta'),
         (4, 8, 'Theta'),
         (8, 12, 'Alpha'),
         (12, 30, 'Beta'),
         (30, 45, 'Gamma')]
######################
# Setting parameters
# Events
event_id = {'odd': 1, 'norm': 2, 'button': 3, 'clear_norm': 4}

# Time range
tmin, tmax = 0.0, 0.8
# n_jobs
n_jobs = 16

######################
# Init stuff
data_id = sys.argv[-1]
# Fetch data_id
# If user input legal data_id, use it
# Else use 'MEG_S02' as fname
if data_id not in stuff_table.keys():
    data_id = 'MEG_S02'
pkl_folder = os.path.join(
    '/nfs/cell_a/userhome/zcc/documents/RSVP_experiment/Project_RSVP_coding_work/MVPA_results')
print(pkl_folder)
if not os.path.exists(pkl_folder):
    os.mkdir(pkl_folder)

stuff = stuff_table[data_id]
for e in stuff.items():
    print(e[0], ':', e[1])

######################
# Read epochs from file
epochs_list = []
group_list = []
for session_id in stuff['session_range']:
    epochs_path = stuff['epochs_path'] % session_id
    print(epochs_path)
    # Read epochs

    _epochs = mne.read_epochs(epochs_path)[['odd', 'clear_norm']]
    # _epochs = mne.read_epochs(epochs_path)[['odd', 'norm', 'clear_norm']]
    # _epochs.events[_epochs.events[:, -1]==4, -1] = 2
    # _epochs = _epochs[['odd', 'norm']]
    _epochs = _epochs.crop(tmin=tmin, tmax=tmax)

    # !!! 'Align' epochs
    if len(epochs_list) > 0:
        _epochs.info['dev_head_t'] = epochs_list[0].info['dev_head_t']

    # Append sessino_id as group idx
    group_list.append(session_id + np.zeros([len(_epochs.events[:, 0]), 1]))
    # Append epochs
    epochs_list.append(_epochs)

######################
# Concatenate epochs in epochs_list
epochs_concatenate = mne.epochs.concatenate_epochs(epochs_list)
groups = np.concatenate(group_list).squeeze()

######################
# MVPA
# Init Cross-validation instance
logo = LeaveOneGroupOut()
# Init Xdawn, classifier and time_decoder
xdawn = mne.preprocessing.Xdawn(n_components=6, reg='diagonal_fixed')

# Init classifier
class_weight = 'balanced'  # None or 'balanced'
lr = LogisticRegression(solver='lbfgs', class_weight=class_weight)
svm = svm.SVC(gamma='scale', kernel='rbf', class_weight=class_weight)

# Init decoder
clf = make_pipeline(StandardScaler(), svm)
# Raw 3-D data decoder
raw_decoder = make_pipeline(mne.decoding.Vectorizer(), clf)
# Time resolution decoder
time_decoder = SlidingEstimator(clf, n_jobs=n_jobs, scoring='f1', verbose=1)

# Init time information
times = epochs_concatenate.times
n_times = len(times)
y_true = epochs_concatenate.events[:, 2]
n_samples = len(y_true)
# Time window information
sfreq = epochs_concatenate.info['sfreq']
time_windows = {}
y_pred_timewindow = {}
# window_length refers time length in seconds
for window_length in [0.05, 0.1, 0.2, 0.3, 0.4]:
    # Length in time points
    w_length = int(sfreq * window_length)
    # Step in time points
    w_step = int(sfreq * window_length / 2)
    # Beginnings in time points
    w_start = np.arange(0, n_times-w_length, w_step)
    # The time stamps of the windows
    w_time = np.empty(len(w_start))
    for j, s in enumerate(w_start):
        w_time[j] = (times[s] + times[s+w_length]) / 2
    # Setup label list for each window_length
    # It is a matrix with size of n_samples x len(w_time)
    y_pred_timewindow[window_length] = np.empty([n_samples, len(w_time)])
    # Storage w_start, w_length, w_time
    time_windows[window_length] = [w_start, w_length, w_time]

######################
# MVPA for each band
for band in bands:
    # Setup parameters
    # stop freq
    l_freq, h_freq = band[0], band[1]
    # pkl_path, pkl file path for storage results
    pkl_path = os.path.join(pkl_folder, '%s-%s.pkl' % (data_id, band[2]))

    # Copy epochs
    epochs = epochs_concatenate.copy()

    # Filter epochs, filter function seems not applied in-place
    epochs = epochs.filter(l_freq=l_freq, h_freq=h_freq,
                           n_jobs=n_jobs, verbose=2)

    # Predicted map
    map_pred = np.zeros(n_samples)
    # Prediction of all time decoding
    y_pred = np.empty(n_samples)
    # Prediction of time resolution decoding
    y_pred_time = np.empty([n_samples, n_times])

    for train_index, test_index in logo.split(y_true, y_true, groups):
        # Cross-validation across groups, groups mean different sessions
        print('=' * 80)
        print(epochs[train_index])
        print(epochs[test_index])

        # Xdawn denoise
        # fit_transform
        X_train = xdawn.fit_transform(epochs[train_index])
        y_train = y_true[train_index]
        # transform
        X_test = xdawn.transform(epochs[test_index])
        y_test = y_true[test_index]

        # All time decoder
        # Fit
        raw_decoder.fit(X_train, y_train)
        # Predict
        y_pred[test_index] = raw_decoder.predict(X_test)

        # Time decoder
        # Fit
        time_decoder.fit(X_train, y_train)
        # Predict
        y_pred_time[test_index] = time_decoder.predict(X_test)

        # Time window decoder
        for window_length, _info in time_windows.items():
            # _info[0], w_start
            # _info[1], w_length
            # _info[2], w_time
            w_length = _info[1]
            for j, w_start in enumerate(_info[0]):
                w_stop = w_start + w_length
                print(w_start)
                # Crop X_train and X_test
                _X_train = X_train[:, :, w_start:w_start+w_length]
                _X_test = X_test[:, :, w_start:w_start+w_length]
                # Fit
                raw_decoder.fit(_X_train, y_train)
                y_pred_timewindow[window_length][
                    test_index, j] = raw_decoder.predict(_X_test)

        # Mark examples that have been tested
        map_pred[test_index] = 1
        print('%d | %d samples solved.' % (sum(map_pred), n_samples))
        print('-' * 80)

    results = dict(
        times=times,
        time_windows=time_windows,
        y_true=y_true,
        y_pred=y_pred,
        y_pred_time=y_pred_time,
        y_pred_timewindow=y_pred_timewindow,
    )

    with open(pkl_path, 'wb') as f:
        pickle.dump(results, f)
