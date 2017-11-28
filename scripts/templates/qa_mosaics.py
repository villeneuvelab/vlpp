#!/usr/bin/env python
# -*- coding: utf-8 -*-


import glob
import json
import os
from jinja2 import Environment, FileSystemLoader
from qamosaic import qamosaic


def save_json(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)


def main():
    # Usefull directories
    os.mkdir("data")

    # Informations
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
    m.save(target)

    # Atlas
    tag = "atlas"
    m = qamosaic.Mosaic(anat, mask=brainmask, overlay=atlas, cmap="gray")
    target = "data/{0}_{1}_mosaic.jpg".format(participant_id, tag)
    m.save(target)

    # Pet
    tag = "pet"
    m = qamosaic.Mosaic(pet, mask=brainmask, contour=cerebellumCortex)
    target = "data/{0}_{1}_mosaic.jpg".format(participant_id, tag)
    m.save(target)

    # Pet Atlas
    tag = "petatlas"
    m = qamosaic.Mosaic(pet, mask=brainmask, overlay=atlas, cmap="gray")
    target = "data/{0}_{1}_mosaic.jpg".format(participant_id, tag)
    participant_info = m.save(target)

    participant_info["participant_id"] = participant_id
    jsonPath = "data/{}_registration_T1w.json".format(participant_id)
    save_json(jsonPath, participant_info)

if __name__ == "__main__":
    main()
