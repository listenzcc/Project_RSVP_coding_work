# coding: utf-8

import mne
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from mk_stuff_table import stuff_table

event_id = {'odd': 1, 'norm': 2, 'button': 3, 'clear_norm': 4}

# stuff = stuff_table['MEG_S02']
for stuff in stuff_table.values():
    for e in stuff.items():
        print(e[0], ':', e[1])

    for session_id in stuff['session_range']:
        print(session_id)

        epochs_path = stuff['epochs_path'] % session_id
        report_path = stuff['evoked_joint_report_path'] % session_id
        epochs = mne.read_epochs(epochs_path)
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
