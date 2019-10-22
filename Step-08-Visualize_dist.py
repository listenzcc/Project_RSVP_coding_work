# coding: utf-8
# filename: Step-08-Visualize_dist.py

from scipy.spatial.distance import cdist
import tqdm
import mne
import numpy as np
import matplotlib.pyplot as plt
from pprint import pprint
from mk_stuff_table import stuff_table
from matplotlib.backends.backend_pdf import PdfPages


######################
# Setting parameters
# Bands
bands = [(0, 4, 'Delta'),
         (4, 8, 'Theta'),
         (8, 12, 'Alpha'),
         (12, 30, 'Beta'),
         (30, 45, 'Gamma')]
# Targe Delta band
band = [e for e in bands if e[-1] == 'Delta'][0]
l_freq, h_freq = band[0], band[1]
# define frequencies of interest (log-spaced)
freqs = np.logspace(*np.log10([1, 4]), num=10)
# different number of cycle per frequency
n_cycles = freqs / 2
# Events
# event_id = {'odd': 1, 'norm': 2, 'button': 3, 'clear_norm': 4}
# event_id = {'odd': 1, 'clear_norm': 4}
# Time range
tmin, tmax = 0.0, 0.8
# n_jobs
n_jobs = 8
# Initialize Xdawn
xdawn = mne.preprocessing.Xdawn(n_components=6, reg='diagonal_fixed')

# Identify data we want
data_id = 'MEG_S02'
stuff = stuff_table[data_id]
# Check the stuff
pprint(stuff)
# Report path
report_path = 'result_%s.pdf'

# Initialize empty epochs_list
epochs_list = []
# For each epochs, read it and append it into epochs_list
for session_id in [4, 6]:  # stuff['session_range']:
    epochs_path = stuff['epochs_path'] % session_id
    print(epochs_path)

    # Read epochs
    _epochs = mne.read_epochs(epochs_path)[['odd', 'button', 'clear_norm']]

    # !!! 'Align' epochs
    if len(epochs_list) > 0:
        _epochs.info['dev_head_t'] = epochs_list[0].info['dev_head_t']

    # Append epochs
    epochs_list.append(_epochs)

# Concatenate epochs in epochs_list
epochs_concatenate = mne.epochs.concatenate_epochs(epochs_list)
# Filter epochs_concatenate
epochs_concatenate = epochs_concatenate.filter(l_freq=l_freq, h_freq=h_freq,
                                               n_jobs=n_jobs, verbose=2)

# Fit xdawn use epochs
xdawn.fit(epochs_concatenate)
# Apply xdawn to denoise
epochs_denoised = xdawn.apply(epochs_concatenate, event_id=['odd'])['odd']

epochs = epochs_denoised.copy()

event_id = {'odd': 1, 'norm': 2, 'button': 3, 'clear_norm': 4}

label = epochs.events[:, -1]
times = epochs.times

print(epochs.get_data().shape)
print(label.shape, np.unique(label))
print(times.shape)

dnn = []
doo = []
dno = []
pbar = tqdm.tqdm(total=len(times))
for j, time in enumerate(times):
    pbar.update(1)
    norm = epochs['clear_norm'].get_data()[:, :, j]
    odd = epochs['odd'].get_data()[:, :, j]

    nn = cdist(norm, norm)
    oo = cdist(odd, odd)
    no = cdist(norm, odd)

    dnn.append(np.mean(nn))
    doo.append(np.mean(oo))
    dno.append(np.mean(no))

pbar.close()

for data, label in zip([dnn, doo, dno], ['nn', 'oo', 'no']):
    plt.plot(times, data, label=label)
plt.legend()
plt.show()
