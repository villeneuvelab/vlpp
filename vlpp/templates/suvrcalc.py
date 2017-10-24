#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import nibabel as nb
import numpy as np


# path
os.mkdir("pet")
os.mkdir("centiloid")
pet = "${pet}"
centiloid = "${centiloid}"
mask = "${mask}"

# inputs
refmaskData = nb.load(mask).get_data()
roiName = ""
for s in mask.split("_"):
    if s.startswith('roi'):
        roiName = s.split("-")[1]

if "${mode}" == "anat":
    inputs = [
            [pet, "pet", "${suffix.petInAnat}"],
            [centiloid, "centiloid", "${suffix.centiloidInAnat}"]
            ]
else:
    inputs = [
            [pet, "pet", "${suffix.petInTpl}"],
            [centiloid, "centiloid", "${suffix.centiloidInTpl}"]
            ]

for path, directory, suffix in inputs:
    image = nb.load(path)
    affine = image.get_affine()
    data = image.get_data()

    # compute
    refData = np.ma.masked_where(refmaskData==0, data, True)
    suvrData = data / refData.mean()

    # save
    output = "{0}/${participant}_ref-{1}_suvr{2}".format(
            directory, roiName, suffix)
    nb.save(nb.Nifti1Image(suvrData, affine), output)
