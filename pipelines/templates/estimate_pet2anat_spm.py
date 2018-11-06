#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
from glob import glob
from vlpp.utils import add_suffix
from vlpp.registration import estimatePet2Anat


def main():
    anat = "${anat}"
    pet = "${pet}"
    output = "${participant}${suffix.pet2anat}"

    if "${transitional}" == "false":
        estimatePet2Anat(pet, anat, output=output)

    else:
        transitionalPet = glob("${transitional}/tmp/*tmp-estimate.nii.gz")[0]
        estimatePet2Anat(pet, transitionalPet, output=output)


if __name__ == '__main__':
    main()

