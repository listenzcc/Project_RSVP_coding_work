# coding: utf-8

import mne
from mne.time_frequency import tfr_morlet
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
event_id = {'odd': 1, 'clear_norm': 4}
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
for session_id in stuff['session_range']:
    epochs_path = stuff['epochs_path'] % session_id
    print(epochs_path)

    # Read epochs
    _epochs = mne.read_epochs(epochs_path)[['odd', 'clear_norm']]

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


def plot_evoked(epochs, name='name', figs=[]):
    print('plotting evoked on time domain.')
    # Initialize times
    times = epochs.times[::20]
    # Initialize ts_args and topomap_args
    ts_args = dict(gfp=True, time_unit='s')
    topomap_args = dict(sensors=False, time_unit='s')
    # Compute evoked
    evoked = epochs.average()

    # Plot joint evoked on dense times
    fig = evoked.plot_joint(title=name, times=times,
                            ts_args=ts_args,
                            topomap_args=topomap_args,
                            show=False)
    figs.append(fig)

    # Plot joint evoked on peak times
    fig = evoked.plot_joint(title=name, times='peaks',
                            ts_args=ts_args,
                            topomap_args=topomap_args,
                            show=False)
    figs.append(fig)

    return figs


def plot_evoked_freq(epochs, name='name', figs=[]):
    print('plotting evoked on frequency domain')
    # Plot overall psd
    f = epochs.plot_psd(fmax=50, show=False)
    f.set_figheight(2.5)
    f.suptitle(name)
    figs.append(f)

    # Plot psd topomaps for Delta, Theta, Alpha, Beta, Gamma band
    f = epochs.plot_psd_topomap(normalize=True, show=False)
    f.set_figheight(2.5)
    f.suptitle(name)
    figs.append(f)

    # Calculate tfr_morlet power and itc
    power, itc = tfr_morlet(epochs, freqs=freqs, n_cycles=n_cycles,
                            use_fft=True, return_itc=True,
                            n_jobs=n_jobs, verbose=1)

    # Plot wavelet power
    f = power.plot_joint(baseline=(-0.2, 0), mode='mean',
                         show=False)
    f.suptitle(name)
    figs.append(f)

    return figs


for event in ['odd', 'clear_norm']:
    print(event)
    # Fetch epochs of event
    epochs = epochs_denoised[event]
    # Initialize empty figs
    figs = []
    # Plots
    plot_evoked(epochs, name=event, figs=figs)
    plot_evoked_freq(epochs, name=event, figs=figs)
    # Print figures in PDF file
    with PdfPages(report_path % event, 'w') as pp:
        for f in figs:
            pp.savefig(f)
    # Close plt bufers
    plt.close('all')
