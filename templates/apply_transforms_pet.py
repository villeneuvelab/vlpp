#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
from subprocess import call
from jinja2 import Environment, FileSystemLoader


#input = "${pet}"
#inputpet = "${participant}${suffix.pet}"
#inputcentiloid = "${participant}${suffix.centiloid}"


# anat space
cmd = "WarpImageMultiTransform 3 {0} {1} {2} -R {3} --use-BSpline".format(
            "${pet}", "tmp.nii.gz", "${pet2anat}", "${anat}")
call(cmd, shell=True)

cmd = "fslmaths tmp.nii.gz -mul ${gmwm} tmp.nii.gz"
call(cmd, shell=True)
cmd = "fslmaths tmp.nii.gz -kernel gauss 2.548 -fmean {0}".format(
        "${participant}${suffix.petInAnat}")
call(cmd, shell=True)


cmd = "WarpImageMultiTransform 3 {0} {1} {2} -R {3} --use-BSpline".format(
            "${centiloid}", "tmp_centiloid.nii.gz", "${pet2anat}", "${anat}")
call(cmd, shell=True)

cmd = "fslmaths tmp_centiloid.nii.gz -mul ${gmwm} tmp_centiloid.nii.gz"
call(cmd, shell=True)
cmd = "fslmaths tmp_centiloid.nii.gz -kernel gauss 2.548 -fmean {0}".format(
        "${participant}${suffix.centiloidInAnat}")
call(cmd, shell=True)


# template space
call("cp ${participant}${suffix.petInAnat} pet.nii.gz", shell=True)
call("gzip -d pet.nii.gz", shell=True)
tags = {
        "anat2tpl": "${anat2tpl}",
        "img": "pet.nii",
        }
j2_env = Environment(
        loader=FileSystemLoader(os.path.join("${baseDir}", "templates")),
        trim_blocks=True)
j2_env.get_template('apply_anat2tpl.m').stream(**tags).dump("apply_anat2tpl_pet.m")
call("matlab -nodisplay < apply_anat2tpl_pet.m", shell=True)
call("gzip rwpet.nii", shell=True)
os.symlink("rwpet.nii.gz", "${participant}${suffix.petInTpl}")

call("cp ${participant}${suffix.centiloidInAnat} centiloid.nii.gz", shell=True)
call("gzip -d centiloid.nii.gz", shell=True)
tags = {
        "anat2tpl": "${anat2tpl}",
        "img": "centiloid.nii",
        }
j2_env = Environment(
        loader=FileSystemLoader(os.path.join("${baseDir}", "templates")),
        trim_blocks=True)
j2_env.get_template('apply_anat2tpl.m').stream(**tags).dump("apply_anat2tpl_centiloid.m")
call("matlab -nodisplay < apply_anat2tpl_centiloid.m", shell=True)
call("gzip rwcentiloid.nii", shell=True)
os.symlink("rwcentiloid.nii.gz", "${participant}${suffix.centiloidInTpl}")
"""
# template space
cmd = "antsApplyTransforms --dimensionality 3 --reference-image {0} --input {1} --output {2} --interpolation BSpline --input-image-type 0 -t {3} -t {4} -t {5}".format(
            "${tpl}", "${pet}", "${participant}${suffix.petInTpl}",
            "${anat2tpl}", "{anat2tpl_aff}", "${pet2anat}",
            )
call(cmd, shell=True)

cmd = "antsApplyTransforms --dimensionality 3 --reference-image {0} --input {1} --output {2} --interpolation BSpline --input-image-type 0 -t {3} -t {4} -t {5}".format(
            "${tpl}", "${centiloid}", "${participant}${suffix.centiloidInTpl}",
            "${anat2tpl}", "{anat2tpl_aff}", "${pet2anat}",
            )
call(cmd, shell=True)
"""

