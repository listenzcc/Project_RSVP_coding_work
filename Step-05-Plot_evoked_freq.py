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
freqs = np.logspace(*np.log10([1, 50]), num=50)
# freqs = np.linspace(1, 50, 50)
# different number of cycle per frequency
n_cycles = freqs / 2
# bands
bands = [(0, 4, 'Delta'),
         (4, 8, 'Theta'),
         (8, 12, 'Alpha'),
         (12, 30, 'Beta'),
         (30, 45, 'Gamma')]

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
        for eid in epochs.event_id.keys():
            # Fetch epochs of certain event
            epo = epochs[eid]
            print(epo)

            # Plot overall psd
            f = epo.plot_psd(fmax=50, show=False)
            f.set_figheight(2.5)
            f.suptitle('%s %s' % (stuff['subject_id'], eid))
            figs.append(f)

            # Plot psd topomaps for Delta, Theta, Alpha, Beta, Gamma band
            f = epo.plot_psd_topomap(normalize=True, show=False)
            f.set_figheight(2.5)
            f.suptitle('%s %s' % (stuff['subject_id'], eid))
            figs.append(f)

            # Calculate tfr_morlet power and itc
            power, itc = tfr_morlet(epo, freqs=freqs, n_cycles=n_cycles,
                                    use_fft=True, return_itc=True)

            # Plot wavelet power
            f = power.plot_joint(baseline=(-0.2, 0), mode='mean',
                                 show=False)
            f.suptitle('%s %s' % (stuff['subject_id'], eid))
            figs.append(f)
            for band in bands:
                f = power.plot_joint(baseline=(-0.2, 0), mode='mean',
                                     fmin=band[0], fmax=band[1],
                                     timefreqs=((0.3, (band[0]+band[1])/2)),
                                     show=False)
                f.suptitle('%s %s %s' % (stuff['subject_id'], eid, band[2]))
                figs.append(f)

        # Print figures in PDF file
        with PdfPages(report_path, 'w') as pp:
            for f in figs:
                pp.savefig(f)

        # Close plt buffer to save resources
        plt.close('all')
