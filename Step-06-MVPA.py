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

######################
# Setting parameters
# Events
event_id = {'odd': 1, 'norm': 2, 'button': 3, 'clear_norm': 4}
# Freq parameters
l_freq, h_freq = 1, 7  # Hz
h_trans_bandwidth = 3  # Hz
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

tmp_path = 'tmp'
pkl_path = os.path.join(tmp_path, data_id + '.pkl')
print(pkl_path)

stuff = stuff_table[data_id]
for e in stuff.items():
    print(e[0], ':', e[1])

######################
# Read epochs from file
epochs_list = []
group_list = []
for session_id in [5, 7]:  # stuff['session_range']:
    epochs_path = stuff['epochs_path'] % session_id
    print(epochs_path)
    # Read epochs
    # Select one option for operation
    # Option 1, fetch odd and clear_norm epochs
    _epochs = mne.read_epochs(epochs_path)[['odd', 'clear_norm']]
    # Option 2, fetch odd, norm and clear_norm epochs
    # _epochs = mne.read_epochs(epochs_path)[['odd', 'norm', 'clear_norm']]
    # _epochs.events[_epochs.events[:, -1] == 4, -1] = 2

    _epochs = _epochs.crop(tmin=0.0, tmax=0.8)

    # !!! 'Align' epochs
    if len(epochs_list) > 0:
        _epochs.info['dev_head_t'] = epochs_list[0].info['dev_head_t']

    # Append sessino_id as group idx
    group_list.append(session_id + np.zeros([len(_epochs.events[:, 0]), 1]))
    # Append epochs
    epochs_list.append(_epochs)

######################
# Concatenate epochs in epochs_list
epochs = mne.epochs.concatenate_epochs(epochs_list)
groups = np.concatenate(group_list).squeeze()
# Filter epochs, filter function seems not applied in-place
epochs = epochs.filter(l_freq=l_freq, h_freq=h_freq,
                       h_trans_bandwidth=h_trans_bandwidth,
                       n_jobs=n_jobs, verbose=2)
# epochs = epochs.apply_baseline(baseline=(-0.2, 0))

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
raw_decoder = make_pipeline(mne.decoding.Vectorizer(), StandardScaler(), clf)
# Time resolution data decoder
time_decoder = SlidingEstimator(clf, n_jobs=n_jobs, scoring='f1', verbose=1)

# Init time information
times = epochs.times
n_times = len(times)
y_true = epochs.events[:, 2]
n_samples = len(y_true)
# Time window information
sfreq = epochs.info['sfreq']
window_info = {}
y_pred_timewindow = {}
for window_length in [0.1, 0.2, 0.3, 0.4]:
    w_length = int(sfreq * window_length)
    w_step = int(sfreq * window_length / 2)
    w_start = np.arange(0, n_times-w_length, w_step)
    w_time = np.empty(len(w_start))
    for j, s in enumerate(w_start):
        w_time[j] = (times[s] + times[s+w_length]) / 2
    y_pred_timewindow[window_length] = np.empty([n_samples, len(w_time)])
    window_info[window_length] = [w_start, w_length, w_time]

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
    for window_length, info in window_info.items():
        length = info[1]
        for j, start in enumerate(info[0]):
            stop = start + length
            print(start)
            # Crop X_train and X_test
            _X_train = X_train[:, :, start:start+w_length]
            _X_test = X_test[:, :, start:start+w_length]
            # Fit
            raw_decoder.fit(_X_train, y_train)
            y_pred_timewindow[window_length][test_index,
                                             j] = raw_decoder.predict(_X_test)

    # Mark examples that are tested
    map_pred[test_index] = 1
    print('%d | %d samples solved.' % (sum(map_pred), n_samples))
    print('-' * 80)

results = dict(
    times=times,
    window_info=window_info,
    y_true=y_true,
    y_pred=y_pred,
    y_pred_time=y_pred_time,
    y_pred_timewindow=y_pred_timewindow,
)

with open(pkl_path, 'wb') as f:
    pickle.dump(results, f)
