#!/usr/bin/env python3
# coding: utf-8


from mayavi import mlab

import os
import mne
import matplotlib.pyplot as plt

print(__doc__)

rawfile_path = os.path.join('d:\\RSVP_MEG_experiment\\rawdata',
                            '20190326_RSVP_MEG_maxuelin',
                            'S02_lixiangTHU_20190326_04.ds')

system = 'CTF 275'
raw = mne.io.read_raw_ctf(rawfile_path)

meg = ['helmet', 'sensors']
fig = mne.viz.plot_alignment(raw.info, trans=None, dig=False, eeg=False,
                             surfaces=[], meg=meg, coord_frame='meg',
                             verbose=True)
text = mlab.title(system)
text.x_position = 0.5
text.y_position = 0.95
text.property.vertical_justification = 'top'
text.property.justification = 'center'
text.actor.text_scale_mode = 'none'
text.property.bold = True
text.property.font_size = 40
mlab.draw(fig)

mlab.show()
