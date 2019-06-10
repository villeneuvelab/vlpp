#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os

from glob import glob
from vlpp.utils import save_json
from jinja2 import Environment, FileSystemLoader
from vlpp.qamosaic import Mosaic



def main():
    # Usefull directories
    os.mkdir("data")

    # Informations
    participant_id = "${sub.sub}"

    # Images Path
    try: tpl = "${tpl}"
    except: tpl = None

    try: anattpl = glob("${sub.anatTpl}")[0]
    except: anattpl = None

    try: centtpl = glob("${sub.centiloid}")[0]
    except: centtpl = None


    """
    # Anat template
    tag = "anattpl"
    m = Mosaic(anattpl, contour=tpl, cmap="gray", rot=0)
    target = "data/{0}_{1}_mosaic.jpg".format(participant_id, tag)
    m.save(target)

    # PET template
    tag = "pettpl"
    m = Mosaic(centtpl, contour=tpl, rot=0)
    target = "data/{0}_{1}_mosaic.jpg".format(participant_id, tag)
    participant_info = m.save(target)
    """

    # Centiloid ROI
    for roi in ["CerebGry", "Pons", "WhlCblBrnStm", "WhlCbl", "ctx"]:
        tag = "cent{}".format(roi)
        roiPath = os.path.join("/project", "ctb-villens", "quarantine",
                "atlas", "Centiloid_Std_VOI", "nifti", "1mm",
                "voi_{}_1mm.nii".format(roi))
        m = Mosaic(centtpl, contour=roiPath, rot=0)
        target = "data/{0}_{1}_mosaic.jpg".format(participant_id, tag)
        participant_info = m.save(target)

    # post
    participant_info["participant_id"] = participant_id
    jsonPath = "data/{}_registration_tpl.json".format(participant_id)
    save_json(jsonPath, participant_info)

if __name__ == "__main__":
    main()
