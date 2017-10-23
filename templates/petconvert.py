#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
from subprocess import call


def splitext_(path):
    for ext in ['.nii.gz']:
        if path.endswith(ext):
            return path[:-len(ext)], path[-len(ext):]
    return os.path.splitext(path)

img = "${img}"
_, ext = splitext_(img)

if ext == ".mnc":
    call("mnc2nii -nii -short {} petconvert.nii".format(img), shell=True)
    call("fslmaths petconvert.nii -nan petconvert.nii.gz", shell=True)
elif ext in [".nii", ".nii.gz"]:
    call("fslmaths {} -nan petconvert.nii.gz".format(img), shell=True)

