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
    tpl = "${tpl}"
    anattpl = glob.glob("${sub.anatTpl}")[0]
    suvr = glob.glob("${sub.suvr}")[0]

    # Anat template
    tag = "anattpl"
    m = qamosaic.Mosaic(anattpl, contour=tpl, cmap="gray", rot=0)
    target = "data/{0}_{1}_mosaic.jpg".format(participant_id, tag)
    m.save(target)

    # PET template
    tag = "pettpl"
    m = qamosaic.Mosaic(suvr, contour=tpl, rot=0)
    target = "data/{0}_{1}_mosaic.jpg".format(participant_id, tag)
    participant_info = m.save(target)

    participant_info["participant_id"] = participant_id
    jsonPath = "data/{}_registration_tpl.json".format(participant_id)
    save_json(jsonPath, participant_info)

if __name__ == "__main__":
    main()
