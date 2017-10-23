#!/usr/bin/env python
# -*- coding: utf-8 -*-


import nibabel as nb
import numpy as np


# inputs
image = nb.load("${pet}")
affine = image.get_affine()
petData = image.get_data()
refmaskData = nb.load("${mask}").get_data()

# compute
refData = np.ma.masked_where(refmaskData==0, petData, True)
suvrData = petData / refData.mean()

# save
roiName = ""
for s in "${mask}".split("_"):
    if s.startswith('roi'):
        roiName = s.split("-")[1]

outputTpl = "${participant}_ref-{0}{1}"
if "${pet}".endswith("${suffix['petInTpl']}"):
    output = outputTpl.format(roiName, "${suffix['suvrInTpl']}")
else:
    output = outputTpl.format(roiName, "${suffix['suvr']}")

nb.save(nb.Nifti1Image(suvrData, affine), output)
