#!/usr/bin/env python
# -*- coding: utf-8 -*-


import csv
import os
from vlpp.utils import add_suffix
from vlpp.operation import computeSuvr, CentiloidStats, meanFromRoi



def main():
    os.mkdir("centiloid")
    os.mkdir("stats")

    pet = "${pet}"
    tracer = "${tracer}"

    roiPath = os.path.join("${centiloidRoiDir}" , "voi_{}_1mm.nii")
    ctxMask = roiPath.format("ctx")

    rsl = [
            ["participant_id"],
            ["${participant}"],
        ]
    for roiName in ["CerebGry", "Pons", "WhlCblBrnStm", "WhlCbl"]:
        mask = roiPath.format(roiName)
        suvr = os.path.join(
                "centiloid", add_suffix(pet, "ref-{}_suvr".format(roiName)))
        centiloid = os.path.join(
                "centiloid", add_suffix(pet, "ref-{}_centiloid".format(roiName)))

        computeSuvr(pet, mask, suvr)
        centiloidStats = CentiloidStats(suvr, tracer, roiName, centiloid)
        centiloidStats.compute()

        rsl[0].append("{}_suvr".format(roiName))
        rsl[1].append(meanFromRoi(suvr, ctxMask))
        rsl[0].append("{}_centiloid".format(roiName))
        rsl[1].append(meanFromRoi(centiloid, ctxMask))


    stats = os.path.join(
                "stats", os.path.basename(pet).replace(".nii.gz", ".tsv"))

    with open(stats, 'wt') as f:
        w = csv.writer(f, delimiter='\t')#, quotechar='"')
        w.writerows(rsl)


if __name__ == '__main__':
    main()

