# -*- coding: utf-8 -*-


import os
from glob import glob
from .utils import run_shell, gzipd, run_matlab, TPL_PATH


def applyWarpImageMultiTransform(_input, ref, mat, output=None):
    if not output:
        output = "tmp.nii.gz"
    cmd = "WarpImageMultiTransform 3 {0} {1} {2} -R {3} --use-BSpline"
    run_shell(cmd.format(_input, output, mat, ref))
    return output


def estimatePet2Anat(pet, anat, output=None,
        mode="estimate", other=None, tag=None):

    def touch(fname, times=None):
        with open(fname, 'a'):
            os.utime(fname, times)

    if not output:
        output = "tmp.nii.gz"

    tags = {
            "ref": gzipd(anat),
            "source": gzipd(pet, copy=True),
            "mode": mode,
            }

    if mode == "estimate":
        run_matlab(os.path.join(TPL_PATH, "estimate_pet2anat.m"), tags,
                "estimate_pet2anat.m")

        os.remove(tags["ref"])
        os.remove(tags["source"])
        touch(output)

    elif mode == "estwrite":
        tags["nbVol"] = 1
        tags["other"] = gzipd(other, copy=True)

        run_matlab(os.path.join(TPL_PATH, "estimate_pet2anat.m"), tags,
                "apply_pet2anat_{}.m".format(tag))

        os.remove(tags["ref"])
        os.remove(tags["source"])
        os.remove(tags["other"])
        os.remove("coreg_" + tags["source"])

        rsl = glob("coreg_*.nii")[0]
        run_shell("gzip {}".format(rsl))
        os.rename(rsl+".gz", output)

    return output


def applyAnat2Tpl(input, warp, interp, tag, output):

    tags = {
            "img": gzipd(input),
            "warp": warp,
            "interp": interp,
            }
    run_matlab(os.path.join(TPL_PATH, "apply_anat2tpl.m"), tags,
            "apply_anat2tpl_{}.m".format(tag))

    rsl = glob("w*.nii")[0]
    run_shell("gzip {}".format(rsl))
    os.rename(rsl+".gz", output)
    os.remove(tags["img"])
    return output


def applyPet2TplAnts(input, output, ref, anat2tpl, anat2tpl_aff, pet2anat):
    """Not use anymore"""
    cmd = "antsApplyTransforms --dimensionality 3 --reference-image {0} --input {1} --output {2} --interpolation BSpline --input-image-type 0 -t {3} -t {4} -t {5}"
    call(cmd.format(ref, input, output, anat2tpl, anat2tpl_aff, pet2anat), shell=True)

