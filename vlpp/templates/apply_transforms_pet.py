#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
from subprocess import call
from jinja2 import Environment, FileSystemLoader


j2_env = Environment(
        loader=FileSystemLoader(os.path.join("${baseDir}", "templates")),
        trim_blocks=True)

def applyPet2Anat(input, output, ref, mat, mask):
    cmd = "WarpImageMultiTransform 3 {0} tmp.nii.gz {1} -R {2} --use-BSpline"
    call(cmd.format(input, mat, ref), shell=True)

    if "${smooth.maskCSF}" == "true":
        cmd = "fslmaths tmp.nii.gz -mul {0} tmp.nii.gz"
        call(cmd.format(mask), shell=True)

    if "${smooth.ignore}" == "true":
        cmd = "fslmaths tmp.nii.gz -fmean {0}"
        call(cmd.format(output), shell=True)
    else:
        try:
            fwhm = ${smooth.fwhm} / 2.3548
        except:
            fwhm = 6 / 2.3548
        cmd = "fslmaths tmp.nii.gz -kernel gauss {0} -fmean {1}"
        call(cmd.format(fwhm, output), shell=True)


def applyAnat2Tpl(input, output, ref, warp, tag, interp=4):
    call("cp {0} imgToTpl.nii.gz".format(input), shell=True)
    call("gzip -d imgToTpl.nii.gz", shell=True)
    tags = {
            "img": "imgToTpl.nii",
            "anat2tpl": warp,
            "ref": ref,
            "interp": interp,
            }
    batch = "apply_anat2tpl_{0}.m".format(tag)
    j2_env.get_template('apply_anat2tpl.m').stream(**tags).dump(batch)
    call("matlab -nodisplay < {0}".format(batch), shell=True)
    call("gzip rwimgToTpl.nii", shell=True)
    os.rename("rwimgToTpl.nii.gz", output)
    os.remove("imgToTpl.nii")
    os.remove("wimgToTpl.nii")


def applyPet2TplAnts(input, output, ref, anat2tpl, anat2tpl_aff, pet2anat):
    """Not use anymore"""
    cmd = "antsApplyTransforms --dimensionality 3 --reference-image {0} --input {1} --output {2} --interpolation BSpline --input-image-type 0 -t {3} -t {4} -t {5}"
    call(cmd.format(ref, input, output, anat2tpl, anat2tpl_aff, pet2anat), shell=True)


def main():
    os.mkdir("pet")
    os.mkdir("centiloid")

    pet = "${pet}"
    centiloid = "${centiloid}"
    anat = "${anat}"
    gwmw = "${gmwm}"
    tpl = "${tpl}"

    pet2anat = "${pet2anat}"
    anat2tpl = "${anat2tpl}"

    petInAnat = os.path.join("pet",
            "${pet}".replace("${suffix.pet}", "_space-anat${suffix.pet}"))
    applyPet2Anat(pet, petInAnat, anat, pet2anat, gwmw)

    centiloidInAnat = os.path.join("centiloid",
            "${centiloid}".replace("${suffix.pet}", "_space-anat${suffix.pet}"))
    applyPet2Anat(centiloid, centiloidInAnat, anat, pet2anat, gwmw)

    petInTpl = os.path.join("pet",
            "${pet}".replace("${suffix.pet}", "_space-tpl${suffix.pet}"))
    applyAnat2Tpl(petInAnat, petInTpl, tpl, anat2tpl, "pet")

    centiloidInTpl = os.path.join("centiloid",
            "${centiloid}".replace("${suffix.pet}", "_space-tpl${suffix.pet}"))
    applyAnat2Tpl(centiloidInAnat, centiloidInTpl, tpl, anat2tpl, "centiloid")


if __name__ == '__main__':
    main()

