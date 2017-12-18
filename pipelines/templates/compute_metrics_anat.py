#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
from vlpp.utils import filename2dict, add_suffix
from vlpp.operation import computeSuvr, ImgStatsFromAtlas


def main():
    os.mkdir("pet")
    os.mkdir("centiloid")
    os.mkdir("stats")

    pet4070 = "${pet4070}"
    pet5070 = "${pet5070}" #centiloid

    mask = "${refmask}"
    maskDict = filename2dict(mask)
    roiName = maskDict["roi"]

    atlas = "${atlas}"

    for img, _dir in zip(
            [pet4070, pet5070],
            ["pet", "centiloid"],
            ):

        suvr = os.path.join(
                _dir, add_suffix(img, "ref-{}_suvr".format(roiName)))
        stats = os.path.join(
                "stats", os.path.basename(suvr).replace(".nii.gz", ".tsv"))

        computeSuvr(img, mask, suvr)
        imgstats = ImgStatsFromAtlas(suvr, atlas, stats)
        imgstats.compute()


if __name__ == '__main__':
    main()

