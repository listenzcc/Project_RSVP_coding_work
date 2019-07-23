#!/usr/bin/env python3
# coding: utf-8

import os
import sys
import webbrowser
import json

###############################
# Reading dir name from newdir
root = 'd:\\RSVP_MEG_experiment'
newdir = os.path.join(root, 'epochs_saver', 'epochs_freq_1.0_50.0')
[print('%s=None,' % e) for e in os.listdir(newdir)]

###############################
# Show ICA components in firefox
# ffpath = 'C:\\Program Files\\Mozilla Firefox\\firefox.exe'
# webbrowser.register('firefox', None, webbrowser.BackgroundBrowser(ffpath), 1)
# [webbrowser.get('firefox').open(os.path.join(newdir, e, 'raw_ica_report.pdf')) for e in os.listdir(newdir)]

###############################
# Record bad ICA components manually, mainly for sop
bad_ICA_components = dict(
    EEG_S01_R01=[0, 3],
    EEG_S01_R02=[0, 4, 7],
    EEG_S01_R03=[0, 4],
    EEG_S01_R04=[0, 3],
    EEG_S01_R05=[0, 1, 4],
    EEG_S01_R06=[0, 3],
    EEG_S01_R07=[0, 3],
    EEG_S01_R08=[0, 3],
    EEG_S01_R09=[0, 2, 4],
    EEG_S01_R10=[0, 1, 2],
    EEG_S02_R01=[0, 5, 13],
    EEG_S02_R02=[0],
    EEG_S02_R03=[0],
    EEG_S02_R04=[0, 3],
    EEG_S02_R05=[0],
    EEG_S02_R06=[0, 4, 11],
    EEG_S02_R07=[0, 2, 6],
    EEG_S02_R08=[0],
    EEG_S02_R09=[0, 7],
    EEG_S02_R10=[0, 4],
    MEG_S01_R04=[0, 3],
    MEG_S01_R05=[0, 2],
    MEG_S01_R06=[0, 5],
    MEG_S01_R07=[0, 2],
    MEG_S01_R08=[0, 2],
    MEG_S01_R09=[0, 4],
    MEG_S01_R10=[0, 2],
    MEG_S02_R04=[3, 19],
    MEG_S02_R05=[3, 18],
    MEG_S02_R06=[9, 17],
    MEG_S02_R07=[2, 18],
    MEG_S02_R08=[5, 17],
    MEG_S02_R09=[3, 17],
    MEG_S02_R10=[0, 18],
    MEG_S02_R11=[1, 9, 20],)

print(bad_ICA_components)

###############################
# Solid bad_ICA_components into json file
# save json file into newdir since the marked soc components are special to certain ICA decompositions
with open(os.path.join(newdir, 'bad_ICA_components.json'), 'w') as f:
    x = json.dumps(bad_ICA_components)
    f.writelines(x)