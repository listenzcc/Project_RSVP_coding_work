#!/usr/bin/env python3
# coding: utf-8

'''
import mne
import os.path as op
from mayavi import mlab

ds_path = op.join('d:/RSVP_MEG_experiment/rawdata/20190326_RSVP_MEG_zhangchuncheng',
                  'S01_lixiangTHU_20190326_04.ds')

raw = mne.io.read_raw_ctf(ds_path)

meg = ['helmet', 'sensors']


fig = mne.viz.plot_alignment(raw.info, trans=None, dig=False, eeg=False,
                             surfaces=[], meg=meg, coord_frame='meg',
                             verbose=True)
'''


import os.path as op

from mayavi import mlab

import mne
from mne.io import read_raw_fif, read_raw_ctf, read_raw_bti, read_raw_kit
from mne.io import read_raw_artemis123
from mne.datasets import sample, spm_face, testing
from mne.viz import plot_alignment

print(__doc__)

raws = {
    'CTF 275': read_raw_ctf(spm_face.data_path() +
                            '/MEG/spm/SPM_CTF_MEG_example_faces1_3D.ds'),
    'lixiang' : read_raw_ctf('/mnt/d/RSVP_MEG_experiment/rawdata/20190326_RSVP_MEG_maxuelin/S02_lixiangTHU_20190326_04.ds')
}

for system, raw in sorted(raws.items()):
    meg = ['helmet', 'sensors']
    # We don't have coil definitions for KIT refs, so exclude them
    if system != 'KIT':
        meg.append('ref')
    fig = plot_alignment(raw.info, trans=None, dig=False, eeg=False,
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
