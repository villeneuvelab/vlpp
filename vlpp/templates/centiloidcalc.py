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


def main():
    os.mkdir("pet")
    os.mkdir("centiloid")
    pet = "${pet}"
    centiloid = "${centiloid}"
    tpl = "${tpl}"
    anat2tpl = "${anat2tpl}"

    #PET
    outputPet = os.path.join("pet", "${pet}".replace(
            "${suffix.suvr}", "${suffix.centiloid}"))
    CentiloidCalc(pet, outputPet)

    outputPetInTpl = outputPet.replace("space-anat", "space-tpl")
    applyAnat2Tpl(outputPet, outputPetInTpl, tpl, anat2tpl, "pet")

    #Centiloid
    outputCentiloid = os.path.join("centiloid", "${centiloid}".replace(
            "${suffix.suvr}", "${suffix.centiloid}"))
    CentiloidCalc(centiloid, outputCentiloid)

    outputCentiloidInTpl = outputCentiloid.replace("space-anat", "space-tpl")
    applyAnat2Tpl(outputCentiloid, outputCentiloidInTpl, tpl, anat2tpl, "centiloid")


if __name__ == '__main__':
    main()


