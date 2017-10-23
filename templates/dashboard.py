#!/usr/bin/env python
# -*- coding: utf-8 -*-


from qamosaic import qamosaic
from jinja2 import Environment, FileSystemLoader
import os


# Dashboard template
templateDir = os.path.join("${workflow.projectDir}", 'templates')
jinja2Env = Environment(
        loader=FileSystemLoader(templateDir),
        trim_blocks=True,
        )
tpl = jinja2Env.get_template('dashboard.html')

# Usefull directories
os.mkdir("data")
os.mkdir("dashboards")

# Informations
mosaics_info = []
participant_id = "${sub.sub}"


# Anat
m = qamosaic.Mosaic("${sub.anat}")
m.mask = "${sub.brainmask}"
#m.contour = None
#m.overlay = None
m.cmap = "gray"

mosaic_file = "data/{}_anat_mosaic.jpg".format(participant_id)
tag = m.save(mosaic_file)
tag.update({
    "title": "T1",
    "notes": "Freesufer T1 in native space",
    "canvas_id": "canvas_anat",
    "sprite": "sprite_anat",
    "mosaic_file": "../" + mosaic_file,
    })
mosaics_info.append(tag)


# Atlas
m = qamosaic.Mosaic("${sub.anat}")
m.mask = "${sub.brainmask}"
#m.contour = None
m.overlay = "${sub.atlas}"
m.cmap = "gray"

mosaic_file = "data/{}_atlas_mosaic.jpg".format(participant_id)
tag = m.save(mosaic_file)
tag.update({
    "title": "T1 and aparc+aseg",
    "notes": "Freesufer T1 in native space with aparc+aseg as overlay",
    "canvas_id": "canvas_atlas",
    "sprite": "sprite_atlas",
    "mosaic_file": "../" + mosaic_file,
    })
mosaics_info.append(tag)


# Pet
m = qamosaic.Mosaic("${sub.pet}")
m.mask = "${sub.brainmask}"
m.contour = "${sub.cerebellumCortex}"
#m.overlay = None
#m.cmap = None

mosaic_file = "data/{}_pet_mosaic.jpg".format(participant_id)
tag = m.save(mosaic_file)
tag.update({
    "title": "PET",
    "notes": "PET image in freesurfer native space",
    "canvas_id": "canvas_pet",
    "sprite": "sprite_pet",
    "mosaic_file": "../" + mosaic_file,
    })
mosaics_info.append(tag)


# Pet Atlas
m = qamosaic.Mosaic("${sub.pet}")
m.mask = "${sub.brainmask}"
#m.contour = None
m.overlay = "${sub.atlas}"
m.cmap = "gray"

mosaic_file = "data/{}_petatlas_mosaic.jpg".format(participant_id)
tag = m.save(mosaic_file)
tag.update({
    "title": "PET and aparc+aseg",
    "notes": "PET image in freesurfer native space with aparc+aseg as overlay",
    "canvas_id": "canvas_petatlas",
    "sprite": "sprite_petatlas",
    "mosaic_file": "../" + mosaic_file,
    })
mosaics_info.append(tag)

# Save Dashboard
tags = {
        "mosaics": mosaics_info,
        "participant_id": participant_id,
        }
htmlCode = tpl.render(**tags)
dashboard_file = "dashboards/{}_dashboard.html".format(participant_id)
with open(dashboard_file, 'w') as f:
    f.write(htmlCode)
