#!/usr/bin/env python
# -*- coding: utf-8 -*-


import nibabel as nb
import numpy as np
from subprocess import call


# input
atlas = nb.load("${atlas}")
atlasData = atlas.get_data()
maskData = np.empty_like(atlasData)

# Compute mask for ${roiName}
for val in ${index}:
    maskData[atlasData == val] = 1

# save
nb.Nifti1Image(
        maskData,
        atlas.affine,
        atlas.header,
        ).to_filename("mask.nii.gz")

# erode
if "${roiName}".endswith("Erode"):
    cmd = "fslmaths mask.nii.gz -ero mask.nii.gz"
    call(cmd, shell=True)

# publish
output = "${participant}_roi-${roiName}${suffix['mask']}"
call("ln -s mask.nii.gz {0}".format(output), shell=True)

