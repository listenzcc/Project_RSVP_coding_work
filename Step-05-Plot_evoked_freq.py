# coding: utf-8

import numpy as np
import mne
from mne.time_frequency import tfr_morlet
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from mk_stuff_table import stuff_table

######################
# Setup parameters
event_id = {'odd': 1, 'norm': 2, 'button': 3, 'clear_norm': 4}
# define frequencies of interest (log-spaced)
freqs = np.logspace(*np.log10([1, 50]), num=20)
# different number of cycle per frequency
n_cycles = freqs / 2

######################
# Read epochs and plot psd topomaps
# stuff = stuff_table['MEG_S02']
for stuff in stuff_table.values():
    # For each subject
    for e in stuff.items():
        print(e[0], ':', e[1])

    for session_id in stuff['session_range']:
        # For each session
        print(session_id)

        # Setup epochs_path and report_path
        epochs_path = stuff['epochs_path'] % session_id
        report_path = stuff['evoked_freq_report_path'] % session_id
        # Read epochs
        epochs = mne.read_epochs(epochs_path)
        print(epochs)

        ######################
        # Plot psd topomaps and store them in figs, a list for figures
        figs = []
        for e in epochs.event_id.keys():
            # Fetch epochs of certain event
            epo = epochs[e]
            print(epo)

            # Plot overall psd
            f = epo.plot_psd(fmax=50, show=False)
            f.set_figheight(2.5)
            f.suptitle('%s %s' % (stuff['subject_id'], e))
            figs.append(f)

            # Plot psd topomaps for Delta, Theta, Alpha, Beta, Gamma band
            f = epo.plot_psd_topomap(normalize=True, show=False)
            f.set_figheight(2.5)
            f.suptitle('%s %s' % (stuff['subject_id'], e))
            figs.append(f)

            # Calculate tfr_morlet power and itc
            power, itc = tfr_morlet(epo, freqs=freqs, n_cycles=n_cycles,
                                    use_fft=True, return_itc=True)

            # Plot wavelet power
            f = power.plot_joint(baseline=(-0.2, 0), mode='mean',
                                 show=False)
            f.suptitle('%s %s' % (stuff['subject_id'], e))
            figs.append(f)

        # Print figures in PDF file
        with PdfPages(report_path, 'w') as pp:
            for f in figs:
                pp.savefig(f)

        # Close plt buffer to save resources
        plt.close('all')
