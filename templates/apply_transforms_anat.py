#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
from subprocess import call
from jinja2 import Environment, FileSystemLoader

call("cp ${anat} anat.nii.gz", shell=True)
call("gzip -d anat.nii.gz", shell=True)
tags = {
        "anat2tpl": "${anat2tpl}",
        "img": "anat.nii",
        }
j2_env = Environment(
        loader=FileSystemLoader(os.path.join("${baseDir}", "templates")),
        trim_blocks=True)
j2_env.get_template('apply_anat2tpl.m').stream(**tags).dump("apply_anat2tpl_anat.m")
call("matlab -nodisplay < apply_anat2tpl_anat.m", shell=True)
call("gzip rwanat.nii", shell=True)
os.symlink("rwanat.nii.gz", "${participant}${suffix.anatInTpl}")

"""
call("cp ${atlas} atlas.nii.gz", shell=True)
call("gzip -d atlas.nii.gz", shell=True)
tags = {
        "anat2tpl": "${anat2tpl}",
        "img": "atlas.nii",
        }
j2_env = Environment(
        loader=FileSystemLoader(os.path.join("${baseDir}", "templates")),
        trim_blocks=True)
j2_env.get_template('apply_anat2tpl.m').stream(**tags).dump("apply_anat2tpl_atlas.m")
call("matlab -nodisplay < apply_anat2tpl_atlas.m", shell=True)
call("gzip rwatlas.nii", shell=True)
os.symlink("rwatlas.nii.gz", "${participant}${suffix.atlasInTpl}")


antsApplyTransforms --dimensionality 3 --reference-image ${tpl} \
    --input ${anat} --output ${participant}${suffix["anatInTpl"]} \
    --interpolation BSpline --input-image-type 0 \
    -t ${anat2tpl} -t {anat2tpl_aff}

antsApplyTransforms --dimensionality 3 --reference-image ${tpl} \
    --input ${atlas} --output ${participant}${suffix["atlasInTpl"]} \
    --interpolation NearestNeighbor --input-image-type 0 \
    -t ${anat2tpl} -t {anat2tpl_aff}
"""

