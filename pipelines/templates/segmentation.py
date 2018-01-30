#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import shutil
from glob import glob
from vlpp.utils import gzipd, run_shell, run_matlab, TPL_PATH


def main():
    for d in ["mask", "transform"]:
        os.mkdir(d)

    tags = {
        "anat": gzipd("${img}"),
        "spmDir": os.path.join("${LOCAL_VL_DIR}", "matlab_tb", "spm", "v12"),
        }
    run_matlab(os.path.join(TPL_PATH, "segmentation.m"), tags, "segmentation.m")

    for c in glob("c*nii"):
        run_shell("gzip {}".format(c))

    for i in range(1,6):
        src = glob("c{}*".format(i))[0]
        dst = "mask/${participant}_roi-c{}${suffix.mask}".format(i)
        shutil.move(src, dst)

    anat2tpl = "transform/${participant}${suffix.anat2tpl}"
    shutil.copy(glob("y_*.nii")[0], anat2tpl)
    run_shell("gzip {}".format(anat2tpl))

    tpl2anat = "transform/${participant}${suffix.tpl2anat}"
    shutil.copy(glob("iy_*.nii")[0], tpl2anat)
    run_shell("gzip {}".format(tpl2anat))


if __name__ == '__main__':
    main()
