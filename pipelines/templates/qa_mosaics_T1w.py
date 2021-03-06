#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os

from glob import glob
from vlpp.utils import save_json
from vlpp.qamosaic import Mosaic


def main():
    # Usefull directories
    os.mkdir("data")

    # Informations
    participant_id = "${sub.sub}"

    # Images Path
    try: anat = glob("${sub.anat}")[0]
    except: anat = None

    try: brainmask = glob("${sub.brainmask}")[0]
    except: brainmask = None

    try: atlas = glob("${sub.atlas}")[0]
    except: atlas = None

    try: pet = glob("${sub.pet}")[0]
    except: pet = None

    try: cerebellumCortex = glob("${sub.cerebellumCortex}")[0]
    except: cerebellumCortex = None

    try: atlasBaker = glob("${sub.atlasBaker}")[0]
    except: atlasBaker = None

    try: suvrBaker = glob("${sub.suvrBaker}")[0]
    except: suvrBaker = None

    # Anat
    tag = "anat"
    m = Mosaic(anat, mask=brainmask, cmap="gray")
    target = "data/{0}_{1}_mosaic.jpg".format(participant_id, tag)
    m.save(target)

    # Atlas
    tag = "atlas"
    m = Mosaic(anat, mask=brainmask, overlay=atlas, cmap="gray")
    target = "data/{0}_{1}_mosaic.jpg".format(participant_id, tag)
    m.save(target)

    # Pet
    tag = "pet"
    m = Mosaic(pet, mask=brainmask, contour=cerebellumCortex)
    target = "data/{0}_{1}_mosaic.jpg".format(participant_id, tag)
    m.save(target)

    # SUVR Baker
    tag = "suvrbaker"
    m = Mosaic(suvrBaker, mask=brainmask)
    target = "data/{0}_{1}_mosaic.jpg".format(participant_id, tag)
    m.save(target)

    # Atlas Baker
    tag = "atlasbaker"
    m = Mosaic(anat, mask=brainmask, overlay=atlasBaker, cmap="gray")
    target = "data/{0}_{1}_mosaic.jpg".format(participant_id, tag)
    m.save(target)

    # Pet Atlas
    tag = "petatlas"
    m = Mosaic(pet, mask=brainmask, overlay=atlas, cmap="gray")
    target = "data/{0}_{1}_mosaic.jpg".format(participant_id, tag)
    participant_info = m.save(target)

    participant_info["participant_id"] = participant_id
    jsonPath = "data/{}_registration_T1w.json".format(participant_id)
    save_json(jsonPath, participant_info)

if __name__ == "__main__":
    main()
