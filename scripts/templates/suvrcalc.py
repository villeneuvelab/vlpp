#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
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
    call("gzip wimgToTpl.nii", shell=True)
    os.rename("wimgToTpl.nii.gz", output)
    os.remove("imgToTpl.nii")
    #os.remove("wimgToTpl.nii")


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
        suvrData = data / np.nanmean(refData)
        nb.save(nb.Nifti1Image(suvrData, affine), self.suvr)


def _roiName(mask):
    roiName = ""
    for _ in mask.split("_"):
        if _.startswith('roi'):
            roiName = _.split("-")[1]
    return roiName


def main():
    os.mkdir("pet")
    #os.mkdir("centiloid")
    pet = "${pet}"
    #centiloid = "${centiloid}"
    mask = "${mask}"
    roiName = _roiName(mask)
    #tpl = "${tpl}"
    #anat2tpl = "${anat2tpl}"

    #PET
    suvrPet = os.path.join("pet", "${pet}".replace(
            "${suffix.pet}", "_ref-{0}${suffix.suvr}".format(roiName)))
    SuvrCalc(pet, mask, suvrPet)

    #suvrPetInTpl = suvrPet.replace("space-anat", "space-tpl")
    #applyAnat2Tpl(suvrPet, suvrPetInTpl, tpl, anat2tpl, "pet")

    #Centiloid
    #suvr5070 = os.path.join("centiloid", "${centiloid}".replace(
            #"${suffix.pet}", "_ref-{0}${suffix.suvr}".format(roiName)))
    #SuvrCalc(centiloid, mask, suvr5070)

    #suvr5070inTpl = suvr5070.replace("space-anat", "space-tpl")
    #applyAnat2Tpl(suvr5070, suvr5070inTpl, tpl, anat2tpl, "5070")


if __name__ == '__main__':
    main()

