# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
# Imports
import mne
from mayavi import mlab


# %%
# Parameters
subject = 'Subject_02'  # This subject name should consistance with FreeSurfer
spacing = 'oct6'  # 4098 sources per hemisphere

# Run 'mne watershed_bem -s [subject]' before continue.


# %%
# Source space
src = mne.setup_source_space(subject, spacing=spacing)
mne.write_source_spaces('%s-%s-src.fif' % (subject, spacing), src)


# %%
# BEM surfaces
model = mne.make_bem_model(subject)
mne.write_bem_surfaces('%s-5120-5120-5120-bem.fif' % subject, model)


# %%
# BEM solution
bem_sol = mne.make_bem_solution(model)
mne.write_bem_solution('%s-5120-5120-5120-bem-sol.fif' % subject, bem_sol)

