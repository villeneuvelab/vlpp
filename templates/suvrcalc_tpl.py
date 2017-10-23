#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
from subprocess import call
from jinja2 import Environment, FileSystemLoader

call("cp ${suvr} suvr.nii.gz", shell=True)
call("gzip -d suvr.nii.gz", shell=True)
tags = {
        "anat2tpl": "${anat2tpl}",
        "img": "suvr.nii",
        }
j2_env = Environment(
        loader=FileSystemLoader(os.path.join("${baseDir}", "templates")),
        trim_blocks=True)
j2_env.get_template('apply_anat2tpl.m').stream(**tags).dump("apply_anat2tpl_suvr.m")
call("matlab -nodisplay < apply_anat2tpl_suvr.m", shell=True)
call("gzip rwsuvr.nii", shell=True)
os.symlink("rwsuvr.nii.gz", "${participant}_ref-${roiName}${suffix.suvrInTpl}")

