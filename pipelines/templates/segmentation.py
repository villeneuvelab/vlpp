#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import shutil
from glob import glob
from vlpp.utils import gzipd, run_shell, run_matlab, TPL_PATH


PARTICIPANT = "${participant}"

def seg_spm12(img, spmDir):
    for d in ["mask", "transform"]:
        os.mkdir(d)

    tags = {
        "anat": gzipd(img),
        "spmDir": spmDir,
        }

    run_matlab(os.path.join(TPL_PATH, "seg_spm12.m"), tags, "segmentation.m")

    for src in glob("c*nii"):
        dst_tpl = "mask/{}_roi-c{}${suffix.mask}".replace(".gz", "")
        dst = dst_tpl.format(PARTICIPANT, src[1])
        shutil.copy(src, dst)
        run_shell("gzip {}".format(dst))

    anat2tpl = "transform/{}_${suffix.anat2tpl}"
    shutil.copy(glob("y_*.nii")[0], anat2tpl)
    run_shell("gzip {}".format(PARTICIPANT, anat2tpl))

    tpl2anat = "transform/{}_${suffix.tpl2anat}"
    shutil.copy(glob("iy_*.nii")[0], tpl2anat)
    run_shell("gzip {}".format(PARTICIPANT, tpl2anat))


def seg_suit(img, spmDir):
    for d in ["suit", "mask", "transform"]:
        os.mkdir(d)

    nii = gzipd(img)
    generic = "img.nii"
    shutil.move(nii, generic)
    tags = {
        "anat": generic,
        "spmDir": spmDir,
        }

    run_matlab(os.path.join(TPL_PATH, "seg_suit.m"), tags, "segmentation.m")


    src = "iCerebellum-SUIT.nii"
    dst = "suit/{}_suit.nii".format(PARTICIPANT)
    shutil.move(src, dst)
    run_shell("gzip {}".format(dst))

    '''
    for src in glob("c*nii"):
        dst_tpl = "mask/{}_type-spm12_roi-c{}${suffix.mask}"
        dst = dst_tpl.format(PARTICIPANT, src[1])
        shutil.copy(src, dst)
        run_shell("gzip {}".format(dst))

    anat2tpl = "transform/{}_type-spm12_${suffix.anat2tpl}"
    shutil.copy(glob("y_*.nii")[0], anat2tpl)
    run_shell("gzip {}".format(PARTICIPANT, anat2tpl))

    tpl2anat = "transform/{}_type-spm12_${suffix.tpl2anat}"
    shutil.copy(glob("iy_*.nii")[0], tpl2anat)
    run_shell("gzip {}".format(PARTICIPANT, tpl2anat))
    '''


def main():
    _type = "${type}"
    img = "${img}"
    spmDir = "${spmDir}"

    if _type == "spm12":
        seg_spm12(img, spmDir)

    elif _type == "suit":
        seg_suit(img, spmDir)


if __name__ == '__main__':
    main()
