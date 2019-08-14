import os
import mne

###############################
# Setup newdir where epochs saved
root = 'd:\\RSVP_MEG_experiment'
newdir = os.path.join(root, 'epochs_saver', 'epochs_freq_1.0_50.0')

###############################
# Setup read_save_stuff
read_save_stuff = {}

read_save_stuff['S01_eeg'] = dict(
    session_range=range(1, 11),
    report_dir=os.path.join(newdir, 'EEG_S01_R%02d'))

read_save_stuff['S02_eeg'] = dict(
    session_range=range(1, 11),
    report_dir=os.path.join(newdir, 'EEG_S02_R%02d'))

read_save_stuff['S01_meg'] = dict(
    session_range=range(4, 11),
    report_dir=os.path.join(newdir, 'MEG_S01_R%02d'))

read_save_stuff['S02_meg'] = dict(
    session_range=range(4, 12),
    report_dir=os.path.join(newdir, 'MEG_S02_R%02d'))


###############################
# Calculate cov

for stuff in read_save_stuff.values():
  # For s01, s02, eeg and meg

  for session_id in stuff['session_range']:
    # For each session
    report_dir = stuff['report_dir'] % session_id 
    print(report_dir)
    print(os.listdir(report_dir))

    # Read epochs
    epochs = mne.read_epochs(os.path.join(report_dir, 'sfreq200_cropn0.2p1.0-epo.fif'))

    # Calculate cov
    cov = mne.compute_covariance(epochs, method='auto')

    # Save cov
    cov.save(os.path.join(report_dir, 'xxx-epo-cov.fif'))