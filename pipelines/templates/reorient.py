#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import shutil
from glob import glob
from vlpp.utils import gzipd, run_shell, run_matlab, TPL_PATH


def main():
    anat = "${anatInputNii}"
    nu = "${nuInputNii}"
    atlas = "${atlasInputNii}"


    dsts = []
    for niigz in [anat, nu, atlas]:
        nii = gzipd(niigz)
        dst = nii.replace("_input_", "_").replace("_copy", "")
        shutil.move(nii, dst)
        dsts.append(dst)

    tags = {
            "anat": dsts[0],
            "nu": dsts[1],
            "atlas": dsts[2],
            }
    if "${config.set_origin_to_centerOfMass}" != "false":
        run_matlab(
                os.path.join(TPL_PATH, "set_origin_to_centerOfMass.m"),
                tags, "set_origin_to_centerOfMass.m")

    for dst in dsts:
        run_shell("gzip {}".format(dst))


if __name__ == '__main__':
    main()
