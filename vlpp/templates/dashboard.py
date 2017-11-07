#!/usr/bin/env python
# -*- coding: utf-8 -*-


import glob
import os
from jinja2 import Environment, FileSystemLoader
from qamosaic import qamosaic


def main():
    # Dashboard template
    templateDir = os.path.join("${workflow.projectDir}", 'templates')
    jinja2Env = Environment(
            loader=FileSystemLoader(templateDir),
            trim_blocks=True,
            )
    #tpl = jinja2Env.get_template('dashboard.html')

    # Usefull directories
    os.mkdir("data")
    os.mkdir("dashboards")

    # Informations
    mosaics_info = {}
    participant_id = "${sub.sub}"

    # Images Path
    anat = glob.glob("${sub.anat}")[0]
    brainmask = glob.glob("${sub.brainmask}")[0]
    atlas = glob.glob("${sub.atlas}")[0]
    pet = glob.glob("${sub.pet}")[0]
    cerebellumCortex = glob.glob("${sub.cerebellumCortex}")[0]

    # Anat
    tag = "anat"
    m = qamosaic.Mosaic(anat, mask=brainmask, cmap="gray")
    target = "data/{0}_{1}_mosaic.jpg".format(participant_id, tag)
    info = m.save(target)
    info.update({
        "title": "T1",
        "notes": "Freesufer T1 in native space",
        "canvas_id": "canvas_{}".format(tag),
        "sprite": "sprite_{}".format(tag),
        "mosaic_file": "../" + target,
        })
    mosaics_info[tag] = info

    # Atlas
    tag = "atlas"
    m = qamosaic.Mosaic(anat, mask=brainmask, overlay=atlas, cmap="gray")
    target = "data/{0}_{1}_mosaic.jpg".format(participant_id, tag)
    info = m.save(target)
    info.update({
        "title": "T1 and aparc+aseg",
        "notes": "Freesufer T1 in native space with aparc+aseg as overlay",
        "canvas_id": "canvas_{}".format(tag),
        "sprite": "sprite_{}".format(tag),
        "mosaic_file": "../" + target,
        })
    mosaics_info[tag] = info

    # Pet
    tag = "pet"
    m = qamosaic.Mosaic(pet, mask=brainmask, contour=cerebellumCortex)
    target = "data/{0}_{1}_mosaic.jpg".format(participant_id, tag)
    info = m.save(target)
    info.update({
        "title": "PET",
        "notes": "PET image in freesurfer native space",
        "canvas_id": "canvas_{}".format(tag),
        "sprite": "sprite_{}".format(tag),
        "mosaic_file": "../" + target,
        })
    mosaics_info[tag] = info

    # Pet Atlas
    tag = "petatlas"
    m = qamosaic.Mosaic(pet, mask=brainmask, overlay=atlas, cmap="gray")
    target = "data/{0}_{1}_mosaic.jpg".format(participant_id, tag)
    info = m.save(target)
    info.update({
        "title": "PET and aparc+aseg",
        "notes": "PET image in freesurfer native space with aparc+aseg as overlay",
        "canvas_id": "canvas_{}".format(tag),
        "sprite": "sprite_{}".format(tag),
        "mosaic_file": "../" + target,
        })
    mosaics_info[tag] = info

    # Save Dashboard
    tags = {
            "info": mosaics_info,
            "participant_id": participant_id,
            }

    jinja2Env.get_template('dashboard.html').stream(**tags).dump(
            "dashboards/{}_dashboard.html".format(participant_id))
    jinja2Env.get_template('participant_id.js').stream(**tags).dump(
            "data/{}.js".format(participant_id))

    #htmlCode = tpl.render(**tags)
    #dashboard_file = "dashboards/{}_dashboard.html".format(participant_id)
    #with open(dashboard_file, 'w') as f:
        #f.write(htmlCode)

if __name__ == "__main__":
    main()
