<!-- filename: workflow.md -->

# Overview

## The _flow_diagram_ shows what have to be done.

![Flow](flow_diagram.svg "Flow")

[Official Documentation](https://mne.tools/stable/overview/cookbook.html#flow-diagram)

# Preprocessing
Preprocessing steps are the left-top part of the _flow_diagram_.
These analysis are performed in channel domain.

## Bad channels identified
Not found bad channels yet.

## Filter on desired passband
Pass band is set to 1.0 ~ 50.0 Hz.
The lower edge chosen is because of ICA (see below).

## Artifacts suppressing
Depress artifacts using [ICA](https://mne.tools/stable/generated/mne.preprocessing.ICA.html?highlight=ica#mne.preprocessing.ICA).
>ICA is sensitive to low-frequency drifts and therefore requires the data to be high-pass filtered prior to fitting. Typically, a cutoff frequency of 1 Hz is recommended.

My dataset contains not ecg channels.

| Script | Description |
|--------|-------------|
| `Step-01-Calculate_ICA_components.py` | ICA decomposition. |
| `Step-02-Mark_bad_ICA_components.py` | Bad components identified and components depressing.|

## Epoching and evoked data

| Script | Description |
|--------|-------------|
| `Step-03-Save_epochs.py` | Get epochs and save them. |
| `Step-04-Plot_evoked.py` | Plot evoked in time series manner. |
| `Step-05-Plot_evoked_freq.py` | Plot evoked in frequency domain manner. |

We also perform [time-frequency analysis](https://mne.tools/stable/auto_examples/time_frequency/plot_time_frequency_simulated.html?highlight=wavelet) in Step-05, using [morlet wavelet](https://mne.tools/stable/generated/mne.time_frequency.tfr_morlet.html#mne.time_frequency.tfr_morlet).

# Source locations
Source location steps are the right-top part of the _flow_diagram_.

These analysis are performed in source domain.

## Anatomical information
Cortical surface reconstruction with [FreeSurfer](https://surfer.nmr.mgh.harvard.edu/fswiki/RecommendedReconstruction).
FreeSurfer is also combained with MNE [(Find how)](https://mne.tools/stable/auto_tutorials/source-modeling/plot_background_freesurfer.html#tut-freesurfer).

| Command | Description |
|--------|-------------|
| `mri_convert` | Convert IMA files into .nii file. IMA files are T1 image  |
| `recon-all` | Perform FreeSurfer analysis pipeline. |

### Setting up the source space
After that we can set up the source space.

1. Creating a suitable decimated dipole grid on the white matter surface.
Using [_mne.setup_source_space()_](https://mne.tools/stable/generated/mne.setup_source_space.html#mne.setup_source_space).
2. Creating the source space file in fif formate. Using [_mne.write_source_spaces()_](https://mne.tools/stable/generated/mne.write_source_spaces.html#mne.write_source_spaces).

>Recommended subdivisions of an icosahedron and an octahedron for the creation of source spaces. The approximate source spacing and corresponding surface area have been calculated assuming a 1000-cm2 surface area per hemisphere.  
>For example, to create the reconstruction geometry for subject='sample' with a ~5-mm spacing between the grid points, say:  
> * _`src = setup_source_space('sample', spacing='oct6')`_  
> * _`write_source_spaces('sample-oct6-src.fif', src)`_  
> * _`src = read_source_spaces('sample-oct6-src.fif')`_  
> * _`mne.viz.plot_alignment('sample', surfaces='white', coord_frame='head', src=src)`_
>
>>|spacing|Sources per hemisphere|Source spacing|Surface area per source|
>>|:-----:|:--------------------:|:------------:|:---------------------:|
>>|'oct5'|1026|9.9|97|
>>|'ico4'|2562|6.2|39|
>>|'oct6'|4098|4.9|24|
>>|'ico5'|10242|3.1|9.8|
>
>_`src`_ is [mne.SourceSpaces](https://mne.tools/stable/generated/mne.SourceSpaces.html#mne.SourceSpaces).
>Represent a list of source space.
>Currently implemented as a list of dictionaries containing the source space information.
>
>>| Paramaters |  |
>>|--------|--------|  
>>| source_spaces | A list of dictionaries containing the source space information. |  
>>| info | Dictionary with information about the creation of the source space file. Has keys _‘working_dir’_ and _‘command_line’_.|

### Creating the BEM model meshes

BEM is [Boundary Element Model](https://mne.tools/stable/overview/implementation.html#bem-model).

BEM can be calculated using the watershed algorithm.
> Its use in MNE environment is facilitated by the script [mne watershed_bem](https://mne.tools/stable/generated/commands.html#gen-mne-watershed-bem).  
After `mne watershed_bem` has completed, the following files appear in the subject's `bem/watershed` directory:  
>
>>| Files |     |
>>|-------|-----|
>>| `<subject>_brain_surface` | The brain surface triangulation. |
>>| `<subject>_inner_skull_surface` | The inner skull triangulation. |
>>| `<subject>_outer_skull_surface` | The outer skull triangulation. |
>>| `<subject>_outer_skin_surface` | The scalp triangulation. |
>>| `bem/watershed/ws` | The brain MRI volume. _(I have not found it yet.)_ |
>>| `bem/<subject>-head.fif` | The scalp surface to fif format |

### Setting the head surface triangulation files

This stage sets up the subject-dependent data for computing the forward solutions:

> _`model = make_bem_model('sample')`_  
> _`write_bem_surfaces('sample-5120-5120-5120-bem.fif', model)`_  
> _where `surfaces` is a list of BEM surfaces that have each been read using [mne.read_surface()](https://mne.tools/stable/generated/mne.read_surface.html#mne.read_surface)_  
> _This step also checks that the input surfaces are complete and that they are topologically correct, i.e., that the surfaces do not intersect and that the surfaces are correctly ordered (outer skull surface inside the scalp and inner skull surface inside the outer skull)._

Using this model, the BEM solution can be computed using [mne.make_bem_solution()](https://mne.tools/stable/generated/mne.make_bem_solution.html#mne.make_bem_solution) as:

> _`bem_sol = make_bem_solution(model)`_  
> _`write_bem_solution('sample-5120-5120-5120-bem-sol.fif', bem_sol)`_  

After the BEM is set up it is advisable to check that the BEM model meshes are correctly positioned using e.g. [mne.viz.plot_alignment()](https://mne.tools/stable/generated/mne.viz.plot_alignment.html#mne.viz.plot_alignment) or [mne.Report](https://mne.tools/stable/generated/mne.Report.html#mne.Report).

# Aligning coordinate frames

The calculation of the forward solution requires knowledge of the relative location and orientation of the MEG/EEG and MRI coordinate systems (see [The head and device coordinate systems](https://mne.tools/stable/overview/implementation.html#head-device-coords)).

The corregistration is stored in `-trans.fif` file.
Use [mne.gui.coregistration()](https://mne.tools/stable/generated/mne.gui.coregistration.html#mne.gui.coregistration) to create.


> The head and device coordinate systems  
![HeadCS](HeadCS.png "HeadCS")  
The MEG/EEG head coordinate system employed in the MNE software is a right-handed Cartesian coordinate system. The direction of x axis is from left to right, that of y axis to the front, and the z axis thus points up.  
The x axis of the head coordinate system passes through the two periauricular or preauricular points digitized before acquiring the data with positive direction to the right. The y axis passes through the nasion and is normal to the x axis. The z axis points up according to the right-hand rule and is normal to the xy plane.  
The origin of the MEG device coordinate system is device dependent. Its origin is located approximately at the center of a sphere which fits the occipital section of the MEG helmet best with x axis axis going from left to right and y axis pointing front. The z axis is, again, normal to the xy plane with positive direction up.