# coding: utf-8

import os
import mne
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from mk_stuff_table import stuff_table

######################
# Setting parameters
# Events
event_id = {'odd': 1, 'norm': 2, 'button': 3, 'clear_norm': 4}
# Freq parameters
freqs_list = [(1, 4), (4, 7), (7, 12), (7, 9), (9, 12)]
# n_jobs
n_jobs = 1

# stuff = stuff_table['MEG_S02']
for stuff in stuff_table.values():
    for e in stuff.items():
        print(e[0], ':', e[1])

    for session_id in stuff['session_range']:
        print(session_id)

        epochs_path = stuff['epochs_path'] % session_id
        _report_path = stuff['evoked_joint_report_path'] % session_id

        dir_name = os.path.dirname(_report_path)
        base_name = os.path.basename(_report_path)

        for freqs in freqs_list:
            l_freq, h_freq = freqs
            report_path = os.path.join(dir_name, 'band_%d_%d_' % (l_freq, h_freq)+base_name)

            epochs = mne.read_epochs(epochs_path)
            epochs = epochs.filter(l_freq=l_freq, h_freq=h_freq,
                                   n_jobs=n_jobs, verbose=2)
            print(epochs)

            figs = []
            for e in epochs.event_id.keys():
                epo = epochs[e]
                print(epo)
                times = epo.times[::20]

                # fig = epo.plot_psd_topomap(n_jobs=8, verbose=2, show=False)
                # fig.suptitle(e)
                # figs.append(fig)

                evoked = epo.average()
                # fig = evoked.plot(gfp=True, spatial_colors=True, show=False)
                # fig.suptitle(e)
                # figs.append(fig)

                # fig = evoked.plot_topomap(times=times, time_unit='s', show=False)
                # fig.suptitle(e)
                # figs.append(fig)

                ts_args = dict(gfp=True, time_unit='s')
                topomap_args = dict(sensors=False, time_unit='s')
                fig = evoked.plot_joint(title=e, times=times,
                                        ts_args=ts_args,
                                        topomap_args=topomap_args,
                                        show=False)
                figs.append(fig)

                fig = evoked.plot_joint(title=e, times='peaks',
                                        ts_args=ts_args,
                                        topomap_args=topomap_args,
                                        show=False)
                figs.append(fig)

            with PdfPages(report_path, 'w') as pp:
                for f in figs:
                    pp.savefig(f)

            plt.close('all')
