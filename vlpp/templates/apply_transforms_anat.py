#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
from subprocess import call
from jinja2 import Environment, FileSystemLoader


j2_env = Environment(
        loader=FileSystemLoader(os.path.join("${baseDir}", "templates")),
        trim_blocks=True)


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


def main():
    anat = "${anat}"
    atlas = "${atlas}"
    tpl = "${tpl}"

    anat2tpl = "${anat2tpl}"

    anatInTpl = "${participant}${suffix.anatInTpl}"
    applyAnat2Tpl(anat, anatInTpl, tpl, anat2tpl, "anat")

    atlasInTpl = "${participant}${suffix.atlasInTpl}"
    #applyAnat2Tpl(atlas, atlasInTpl, tpl, anat2tpl, "atlas", 0)


if __name__ == '__main__':
    main()

