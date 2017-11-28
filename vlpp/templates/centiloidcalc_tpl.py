#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import json
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

    def __init__(self, input, output):
        self.input = input
        self.output = output
        self.tracer = "${tracer}"
        self._run()


    def _run(self):
        image = nb.load(self.input)
        affine = image.get_affine()
        data = image.get_data()

        # compute
        maskedData = np.ma.masked_where(data==0, data, True)

        if self.tracer == "PIB":
            centiloidData = ((maskedData - 1.009) * 100) / 1.067
        elif self.tracer == "NAV":
            centiloidData = ((maskedData - 1.028) * 100) / 1.174

        nb.save(nb.Nifti1Image(centiloidData, affine), self.output)

class SuvrCalc(object):

    def __init__(self, input, mask, suvrOutput):
        self.input = input
        self.mask = mask
        self.suvr = suvrOutput
        self._run()


    def _run(self):
        maskData = nb.load(self.mask).get_data()

        image = nb.load(self.input)
        affine = image.get_affine()
        data = image.get_data()

        # compute
        refData = np.ma.masked_where(maskData==0, data, True)
        suvrData = data / refData.mean()
        nb.save(nb.Nifti1Image(suvrData, affine), self.suvr)


def main():
    os.mkdir("centiloid")
    pet = "${pet}"

    roiPath = os.path.join("/sf1", "project", "yai-974-aa", "local",
            "atlas", "Centiloid_Std_VOI", "nifti", "1mm",
            "voi_{}_1mm.nii")

    rsl = {}
    for roiName in ["CerebGry", "Pons", "WhlCblBrnStm", "WhlCbl"]:
        mask = roiPath.format(roiName)
        suvrPet = os.path.join("centiloid", pet.replace(
            "${suffix.pet}", "_ref-{0}${suffix.suvr}".format(roiName)))
        SuvrCalc(pet, mask, suvrPet)

        volData = nb.load(suvrPet).get_data()
        print(volData.shape)
        maskData = nb.load(roiPath.format("ctx")).get_data()
        print(maskData.shape)
        data = np.ma.masked_where(maskData==0, volData, True)
        rsl[roiName] = "{0:.4f}".format(data.mean())

    jsonPath = os.path.join("centiloid", pet.replace(
            "${suffix.pet}", "_roi-ctx_suvr.json"))
    with open(jsonPath, 'w') as f:
        json.dump(rsl, f, indent=4)


if __name__ == '__main__':
    main()


