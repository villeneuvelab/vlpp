#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import shutil
from glob import glob
from vlpp.utils import gzipd, run_shell, run_matlab, TPL_PATH


def main():
    niigz = "${petInputNii}"

    nii = gzipd(niigz)
    dst = nii.replace("_input_", "_").replace("_copy", "")
    shutil.move(nii, dst)

    tags = {
            "pet": dst,
            }
    #if "${config.set_origin_to_centerOfMass_pet}" == "true":
    if False:
        run_matlab(
                os.path.join(TPL_PATH, "set_origin_to_centerOfMass_pet.m"),
                tags, "set_origin_to_centerOfMass.m")

    run_shell("gzip {}".format(dst))


if __name__ == '__main__':
    main()
