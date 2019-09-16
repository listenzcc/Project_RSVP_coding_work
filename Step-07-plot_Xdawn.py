# coding: utf-8

import os
import mne
import numpy as np

from mk_stuff_table import stuff_table

bands = [(0, 4, 'Delta'),
         (4, 8, 'Theta'),
         (8, 12, 'Alpha'),
         (12, 30, 'Beta'),
         (30, 45, 'Gamma')]
######################
# Setting parameters
# Events
event_id = {'odd': 1, 'norm': 2, 'button': 3, 'clear_norm': 4}
# Time range
tmin, tmax = 0.0, 0.8
# n_jobs
n_jobs = 8
