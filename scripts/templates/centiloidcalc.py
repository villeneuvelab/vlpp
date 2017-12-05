#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import json
import csv
import nibabel as nb
import numpy as np
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



class CentiloidCalc(object):

    def __init__(self, input, mask, suvrOutput, centOutput):
        self.input = input
        self.mask = mask
        self.suvr = suvrOutput
        self.cent = centOutput
        self.tracer = "${tracer}"
        self._run()


    def _run(self):
        maskData = nb.load(self.mask).get_data()

        image = nb.load(self.input)
        affine = image.get_affine()
        data = image.get_data()

        # compute SUVR
        refData = np.ma.masked_where(maskData==0, data, True)
        #refData[data<=0] = np.nan
        suvrData = data / np.nanmean(refData)
        nb.save(nb.Nifti1Image(suvrData, affine), self.suvr)

        # compute Centiloid
        save = True
        if self.tracer == "PIB":
            centiloidData = ((suvrData - 1.009) * 100) / 1.067
        elif self.tracer == "NAV":
            centiloidData = ((suvrData - 1.028) * 100) / 1.174
        else:
            save = False

        if save and self.cent is not None:
            nb.save(nb.Nifti1Image(centiloidData, affine), self.cent)


def main():
    os.mkdir("centiloid")
    pet = "${pet}"

    roiPath = os.path.join("/sf1", "project", "yai-974-aa", "local",
            "atlas", "Centiloid_Std_VOI", "nifti", "1mm",
            "voi_{}_1mm.nii")

    rsl = [
            ["participant_id"],
            ["${participant}"],
        ]
    for roiName in ["CerebGry", "Pons", "WhlCblBrnStm", "WhlCbl"]:
        mask = roiPath.format(roiName)
        suvrPet = os.path.join("centiloid", pet.replace(
            "${suffix.pet}", "_ref-{0}${suffix.suvr}".format(roiName)))
        centiloidPet = os.path.join("centiloid", pet.replace(
            "${suffix.pet}", "_ref-{0}${suffix.centiloid}".format(roiName)))

        if roiName != "WhlCbl":
            centiloidPet = None
        CentiloidCalc(pet, mask, suvrPet, centiloidPet)

        suvrData = nb.load(suvrPet).get_data()
        maskData = nb.load(roiPath.format("ctx")).get_data()
        suvrData = np.ma.masked_where(maskData==0, suvrData, True)
        rsl[0].append("{}_suvr".format(roiName))
        rsl[1].append("{0:.4f}".format(np.nanmean(suvrData)))

        if centiloidPet:
            centData = nb.load(centiloidPet).get_data()
            centData = np.ma.masked_where(maskData==0, centData, True)
            rsl[0].append("{}_centiloid".format(roiName))
            rsl[1].append("{0:.4f}".format(np.nanmean(centData)))

    csvPath = os.path.join("centiloid", pet.replace(
            "${suffix.pet}", "_roi-ctx.csv"))

    with open(csvPath, 'wt') as csvfile:
        w = csv.writer(csvfile)#, delimiter=',', quotechar='"')
        w.writerows(rsl)



if __name__ == '__main__':
    main()


