#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import nibabel as nb
import numpy as np
from subprocess import call


class SuvrCalc(object):

    def __init__(self, input, mask, suvrOutput,
            tracer=None, centiloidOutput=None):
        self.input = input
        self.mask = mask
        self.suvr = suvrOutput
        self.centiloid = centiloidOutput
        self.tracer = tracer
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

        # centiloid
        if self.centiloid:
            if self.tracer == "PIB":
                centiloidData = ((suvrData - 1.009) * 100) / 1.067
                nb.save(nb.Nifti1Image(centiloidData, affine), self.centiloid)
            elif self.tracer == "NAV":
                centiloidData = ((suvrData - 1.028) * 100) / 1.174
                nb.save(nb.Nifti1Image(centiloidData, affine), self.centiloid)


def _roiName(mask):
    roiName = ""
    for _ in mask.split("_"):
        if _.startswith('roi'):
            roiName = _.split("-")[1]
    return roiName


def main():
    os.mkdir("pet")
    os.mkdir("centiloid")
    pet = "${pet}"
    centiloid = "${centiloid}"
    mask = "${mask}"
    roiName = _roiName(mask)
    tracer = "${tracer}"

    #PET
    suvrPet = os.path.join("pet", "${pet}".replace(
            "${suffix.pet}", "_ref-{0}${suffix.suvr}".format(roiName)))
    SuvrCalc(pet, mask, suvrPet)

    #Centiloid
    suvr5070 = os.path.join("centiloid", "${centiloid}".replace(
            "${suffix.pet}", "_ref-{0}${suffix.suvr}".format(roiName)))
    centiloidOutput = os.path.join("centiloid", "${centiloid}".replace(
            "${suffix.pet}", "_ref-{0}${suffix.centiloid}".format(roiName)))
    SuvrCalc(centiloid, mask, suvr5070, tracer, centiloidOutput)


if __name__ == '__main__':
    main()

