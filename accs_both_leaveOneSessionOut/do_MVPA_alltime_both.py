# coding: utf-8
'''
This script is to do MVPA on MEG RSVP dataset
'''

import matplotlib.pyplot as plt
import mne
import numpy as np
import os
from sklearn import svm
from sklearn.linear_model import LogisticRegression
from sklearn.decomposition import PCA
from sklearn.metrics import classification_report
from sklearn.model_selection import StratifiedKFold, LeaveOneGroupOut
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import MinMaxScaler
import time
import pdb

'''
# Function: Setting MVPA stuff.
# Output: cv, cross-validation maker.
# Output: pca_pipeline, pipeline of pca decomposition.
# Output: xdawn_pipeline, pipeline of xdawn filter.
# Output: clf_*, classifier of svm and lr.
'''

pca = make_pipeline(mne.decoding.Vectorizer(), PCA(n_components=8))

xdawn = mne.preprocessing.Xdawn(n_components=8)

cv = StratifiedKFold(n_splits=10, shuffle=True)
logo = LeaveOneGroupOut()

normalize_pipeline = make_pipeline(mne.decoding.Vectorizer(), MinMaxScaler())

clf_svm_rbf = svm.SVC(gamma='scale', kernel='rbf', class_weight='balanced', verbose=True)


def report_results(true_label, pred_label, title=None):
        print(title)
        report = classification_report(true_label, pred_label, target_names=['odd', 'norm'])
        print(report)
        if title is None:
            return
        with open(os.path.join(results_dir, '%s.txt' % title), 'w') as f:
            f.writelines(report)


'''
# Function: Setting evrionment for the script.
# Output: root_path, directory of project.
# Output: time_stamp, string of beginning time of the script.
# Output: results_dir, directory for storing results.
'''
root_dir = os.path.join('/nfs/cell_a/userhome/zcc/documents/RSVP_experiment/')
time_stamp = time.strftime('%Y-%m-%d-%H-%M-%S')
results_dir = os.path.join(root_dir, 'RSVP_MVPA', 'MVPA_across_session')
epochs_dir = os.path.join(root_dir, 'epochs_saver', 'epochs_freq_1.0_50.0')

read_save_stuff = {}

read_save_stuff['S01_eeg'] = dict(
        range_run   = range(1, 11),
        epochs_path = os.path.join(epochs_dir, 'EEG_S01_R%02d', 'sfreq200_cropn0.2p1.0-epo.fif'),
        report_path = os.path.join(results_dir, 'accs_eeg_S01.txt'))

read_save_stuff['S02_eeg'] = dict(
        range_run   = range(1, 11),
        epochs_path = os.path.join(epochs_dir, 'EEG_S02_R%02d', 'sfreq200_cropn0.2p1.0-epo.fif'),
        report_path = os.path.join(results_dir, 'accs_eeg_S02.txt'))

read_save_stuff['S01_meg'] = dict(
        range_run   = range(4, 11),
        epochs_path = os.path.join(epochs_dir, 'MEG_S01_R%02d', 'sfreq200_cropn0.2p1.0-epo.fif'),
        report_path = os.path.join(results_dir, 'accs_meg_S01.txt'))

read_save_stuff['S02_meg'] = dict(
        range_run   = range(4, 12),
        epochs_path = os.path.join(epochs_dir, 'MEG_S02_R%02d', 'sfreq200_cropn0.2p1.0-epo.fif'),
        report_path = os.path.join(results_dir, 'accs_meg_S02.txt'))


for stuff in read_save_stuff.values():
    print('-'*80)
    for e in stuff.items():
        print(e[0], e[1])

    '''
    # Function: Reading epochs.
    '''
    labels = None
    epochs_list = []
    _groups = []
    for i in stuff['range_run']:
        # Function: Reading epochs from -epo.fif.
        epo_path = os.path.join(stuff['epochs_path'] % i)

        epochs = mne.read_epochs(epo_path, verbose=True)
        epochs = epochs[['odd', 'norm']]
        epochs.crop(tmin=0.0, tmax=1.0)

        # Attention!!!
        # This may cause poor alignment between epochs.
        # But this is necessary for concatenate_epochs.
        if epochs_list.__len__() != 0:
            epochs.info['dev_head_t'] = epochs_list[0].info['dev_head_t']

        # Storage epochs into epochs_list
        epochs_list.append(epochs)

        # Record i as group idx
        _groups.append(i + np.zeros([len(epochs.events[:, -1]), 1]))

    epochs = mne.epochs.concatenate_epochs(epochs_list)
    epochs_data = epochs.get_data()
    epochs_labels = epochs.events[:, -1]
    epochs_groups = np.concatenate(_groups).squeeze()

    '''
    # Function: Repeat training and testing.
    # Output:
    '''
    sfreq = epochs.info['sfreq']
    w_length = int(sfreq * 0.1)   # running classifier: window length
    w_step = int(sfreq * 0.05)  # running classifier: window step size
    w_start = np.arange(0, epochs.get_data().shape[2] - w_length, w_step)


    # init preds results.
    preds_xdawn_svm_rbf = np.empty(len(epochs_labels))

    for train, test in logo.split(epochs_data, epochs_labels, epochs_groups):
        print('-' * 80)

        label_train = epochs_labels[train]
        label_test = epochs_labels[test]

        # xdawn
        data_train = normalize_pipeline.fit_transform(xdawn.fit_transform(epochs[train]))
        data_test = normalize_pipeline.transform(xdawn.transform(epochs[test]))

        # SVM rbf
        clf_svm_rbf.fit(data_train, label_train)
        preds_xdawn_svm_rbf[test] = clf_svm_rbf.predict(data_test)


    '''
    # Function: Save report into file.
    '''
    fpath = os.path.join(stuff['report_path'])


    with open(fpath, 'w') as f:
        report_svm_rbf = classification_report(preds_xdawn_svm_rbf, epochs_labels, target_names=['odd', 'norm'])
        print(report_svm_rbf)
        f.writelines('\n%s\n' % os.path.basename(fpath))
        f.writelines(report_svm_rbf)

