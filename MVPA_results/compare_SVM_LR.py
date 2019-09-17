# coding: utf-8

import os
import pickle
import itertools
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from sklearn.metrics import classification_report, f1_score


data_ids = ['EEG_S01', 'EEG_S02', 'MEG_S01', 'MEG_S02']
cls_names = ['lr', 'svm', 'lr_accum', 'svm_accum']
band_names = ['Delta']
pdf_path = 'acc_compare.pdf'
figs = []
for id, cls, band in itertools.product(data_ids, cls_names, band_names):
    pkl_file_name = os.path.join(cls, id + '-' + band + '.pkl')
    print(pkl_file_name)
    if not os.path.exists(pkl_file_name):
        continue

    # Read file
    with open(pkl_file_name, 'rb') as f:
        results = pickle.load(f)

    # Fetch results
    times = results['times']
    window_info = results['time_windows']
    y_true = results['y_true']
    y_pred = results['y_pred']
    y_pred_time = results['y_pred_time']
    y_pred_timewindow = results['y_pred_timewindow']
    num_sample = len(y_true)
    num_time = len(times)

    # Report
    fig, axes = plt.subplots(2, 1)

    # All time
    report = classification_report(y_true, y_pred,
                                   target_names=['odd', 'norm'])
    axes[0].text(0.1, 0.1, report, family='monospace')
    print(report)

    legend = []
    # Time resolution
    f1_time = np.empty([num_time, 2])
    for j in range(num_time):
        f1_time[j] = f1_score(y_true, y_pred_time[:, j], average=None)
    axes[1].plot(times, f1_time, marker='.')
    legend.append('odd')
    legend.append('norm')

    # Time window
    for win_length, win_info in window_info.items():
        window_times = win_info[2]
        num_timewindow = len(window_times)
        f1_tmp = np.empty([num_timewindow, 2])
        for j in range(num_timewindow):
            f1_tmp[j] = f1_score(
                y_true, y_pred_timewindow[win_length][:, j], average=None)
        axes[1].plot(window_times, f1_tmp, marker='.')
        legend.append('odd')
        legend.append('norm')

    # Append fig
    axes[1].legend(legend)
    fig.suptitle(pkl_file_name)
    figs.append(fig)

with PdfPages(pdf_path, 'w') as pp:
    for f in figs:
        pp.savefig(f)

plt.close('all')
