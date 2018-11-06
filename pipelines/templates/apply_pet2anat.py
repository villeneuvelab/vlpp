#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
from glob import glob
from vlpp.utils import add_suffix, nfmap2dict, warn, run_shell
from vlpp.registration import applyWarpImageMultiTransform, estimatePet2Anat


def main():
    transitional = "${transitional}"
    mode = "${config.pet2anat.mode}"

    os.mkdir("pet")
    os.mkdir("centiloid")
    os.mkdir("tmp")

    pet4070 = "${pet4070}"
    pet5070 = "${pet5070}" #centiloid
    pet2anat = "${pet2anat}"

    anat = "${anat}"
    brain = "${brain}"
    gmwm = "${gmwm}"

    petParams = nfmap2dict("${pet2anatPetParams}")
    centiloidParams = nfmap2dict("${pet2anatCentiloidParams}")
    tmpParams = {
            "mask": "null",
            "fwhm": 6,
            }

    for pet, _dir, params in zip(
            [pet4070, pet5070, pet4070],
            ["pet", "centiloid", "tmp"],
            [petParams, centiloidParams, tmpParams],
            ):

        output = os.path.join(_dir, add_suffix(pet, "space-anat"))

        # Apply transform
        if transitional != "false":
            transitPet = glob(
                    "{}/tmp/*tmp-estimate.nii.gz".format(transitional))[0]
            transit2anat = glob(
                    "{}/transform/*${suffix.pet2anat}".format(transitional))[0]
            petInTransit = applyWarpImageMultiTransform(
                    pet, transitPet, pet2anat, "petInTransit.nii.gz")
            petTemp = applyWarpImageMultiTransform(
                    petInTransit, anat, transit2anat)

        else:
            if mode == "ants":
                petTemp = applyWarpImageMultiTransform(pet, anat, pet2anat)
            elif mode == "spm":
                petToEstimate = "${petToEstimate}"
                petTemp = estimatePet2Anat(
                        petToEstimate, anat, mode="estwrite", other=pet, tag=_dir)

        # Masking step
        mask = params["mask"]
        cmd = "fslmaths {0} -mul {1} {0}"
        if mask == "brain":
            run_shell(cmd.format(petTemp, brain))

        elif mask == "gmwm":
            run_shell(cmd.format(petTemp, gmwm))

        elif mask == "null":
            pass

        else:
            warn([
                "Process: apply_pet2anat",
                "  {} option to mask {} data is not supported".format(
                    mask, pet),
                "  See default configuration for more information",
                "  {} data won't be masked".format(pet),
                ])

        # Smoothing step
        fwhm = params["fwhm"]
        try:
            sigma = int(fwhm) / 2.3548
            if sigma > 0:
                cmd = "fslmaths {0} -kernel gauss {1} -fmean {2}"
                run_shell(cmd.format(petTemp, sigma, output))
            else:
                cmd = "fslmaths {0} -fmean {1}"
                run_shell(cmd.format(petTemp, output))

        except:
            warn([
                "Process: apply_pet2anat",
                "  {} is not an integer".format(fwhm),
                "  {} data won't be smoothed".format(pet),
                ])
            cmd = "fslmaths {0} -fmean {1}"
            run_shell(cmd.format(petTemp, output))


if __name__ == '__main__':
    main()

