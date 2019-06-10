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

    try: pet = glob("${sub.pet}")[0]
    except: pet = None

    try: suit = glob("${sub.suit}")[0]
    except: suit = None

    # Anat
    tag = "suitAnat"
    m = Mosaic(anat, mask=suit, overlay=suit, cmap="gray")
    target = "data/{0}_{1}_mosaic.jpg".format(participant_id, tag)
    m.save(target, suit=True)

    # Pet
    tag = "suitPet"
    m = Mosaic(pet, mask=suit, overlay=suit)
    target = "data/{0}_{1}_mosaic.jpg".format(participant_id, tag)
    participant_info = m.save(target, suit=True)

    participant_info["participant_id"] = participant_id
    jsonPath = "data/{}_registration_suit.json".format(participant_id)
    save_json(jsonPath, participant_info)

if __name__ == "__main__":
    main()
