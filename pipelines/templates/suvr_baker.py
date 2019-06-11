#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import shutil
#from glob import glob
from vlpp.utils import gzipd, run_matlab, TPL_PATH, add_suffix, run_shell
from vlpp.operation import ImgStatsFromAtlas



def main():
    for d in ["baker", "stats"]:
        os.mkdir(d)

    tags = {
        "bakerDir": "${bakerDir}",
        "atlas": gzipd("${atlas}"),
        "pet": gzipd("${pet4070}"),
        "gmSpm": gzipd("${gmSpm}"),
        "wmSpm": gzipd("${wmSpm}"),
        "csfSpm": gzipd("${csfSpm}"),
        "boneSpm": gzipd("${boneSpm}"),
        "softSpm": gzipd("${softSpm}"),
        "atlasCereb": gzipd("${atlasCereb}"),
        "scannerResolution": "${scannerResolution}",
        }

    run_matlab(os.path.join(TPL_PATH, "suvr_baker.m"), tags, "suvr_baker.m")

    #atlas
    src = "FINAL0_edited_aparc+aseg.nii"
    dst = os.path.join("baker", add_suffix(tags["atlas"], "edited-baker"))
    dst = dst.replace("_copy", "")
    shutil.copy(src, dst)
    run_shell("gzip {}".format(dst))

    #suvr
    src = "FINAL0_suvr_normalized_infcereg.nii"
    dst = os.path.join("baker", add_suffix(tags["pet"], "ref-infcereg_suvr"))
    suvr = dst.replace("_copy", "")
    shutil.copy(src, suvr)
    run_shell("gzip {}".format(suvr))
    suvr = suvr + ".gz"

    #stat
    stats = os.path.join(
            "stats", os.path.basename(suvr).replace(".nii.gz", ".tsv"))
    atlas = "${atlas}"
    imgstats = ImgStatsFromAtlas(suvr, atlas, stats)
    imgstats.compute()

    #roigroups
    src = "FINAL0_roigroups.mat"
    dst = os.path.join(
            "baker", add_suffix(tags["pet"], "pvc-rousset"))
    dst = dst.replace("_copy", "").replace(".nii", ".mat")
    shutil.copy(src, dst)


if __name__ == '__main__':
    main()

