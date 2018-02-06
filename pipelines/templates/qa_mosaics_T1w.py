#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os

from glob import glob
from vlpp.utils import save_json
from qamosaic import qamosaic


def main():
    # Usefull directories
    os.mkdir("data")

    # Informations
    participant_id = "${sub.sub}"

    # Images Path
    anat = glob("${sub.anat}")[0]
    brainmask = glob("${sub.brainmask}")[0]
    atlas = glob("${sub.atlas}")[0]
    pet = glob("${sub.pet}")[0]
    cerebellumCortex = glob("${sub.cerebellumCortex}")[0]
    atlasBaker = glob("${sub.atlasBaker}")[0]
    suvrBaker = glob("${sub.suvrBaker}")[0]

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

    # SUVR Baker
    tag = "suvrbaker"
    m = qamosaic.Mosaic(suvrBaker, mask=brainmask)
    target = "data/{0}_{1}_mosaic.jpg".format(participant_id, tag)
    m.save(target)

    # Atlas Baker
    tag = "atlasbaker"
    m = qamosaic.Mosaic(anat, mask=brainmask, overlay=atlasBaker, cmap="gray")
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
