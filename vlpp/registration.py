# -*- coding: utf-8 -*-


import os
from glob import glob
from .utils import run_shell, gzipd, run_matlab


def applyWarpImageMultiTransform(input, ref, mat, output=None):
    if not output:
        output = "tmp.nii.gz"
    cmd = "WarpImageMultiTransform 3 {0} {1} {2} -R {3} --use-BSpline"
    run_shell(cmd.format(input, output, mat, ref))
    return output


def applyAnat2Tpl(input, warp, interp, tag, output):

    tags = {
            "img": gzipd(input),
            "warp": warp,
            "interp": interp,
            }
    run_matlab("apply_anat2tpl.m", tags, "apply_anat2tpl_{}.m".format(tag))

    rsl = glob("w*.nii")[0]
    run_shell("gzip {}".format(rsl))
    os.rename(rsl+".gz", output)
    os.remove(tags["img"])
    return output


def applyPet2TplAnts(input, output, ref, anat2tpl, anat2tpl_aff, pet2anat):
    """Not use anymore"""
    cmd = "antsApplyTransforms --dimensionality 3 --reference-image {0} --input {1} --output {2} --interpolation BSpline --input-image-type 0 -t {3} -t {4} -t {5}"
    call(cmd.format(ref, input, output, anat2tpl, anat2tpl_aff, pet2anat), shell=True)

