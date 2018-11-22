#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
from glob import glob
from vlpp.utils import add_suffix, nfmap2dict, warn, run_shell, gzipd, run_matlab, TPL_PATH
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

    petToEstimate = "${petToEstimate}"
    if "${config.set_origin_to_centerOfMass_pet}" == "true":

        dsts = []
        for niigz in [petToEstimate, pet4070, pet5070]:
            nii = gzipd(niigz)
            #dst = nii.replace("_input_", "_").replace("_copy", "")
            #shutil.move(nii, dst)
            #dsts.append(dst)
            dsts.append(nii)

        tags = {
                "petToEstimate": dsts[0],
                "pet4070": dsts[1],
                "pet5070": dsts[2],
                }
        run_matlab(
                os.path.join(TPL_PATH, "set_origin_to_centerOfMass_pet.m"),
                tags, "set_origin_to_centerOfMass.m")

        for dst in dsts:
            run_shell("gzip {}".format(dst))

        petToEstimate = dsts[0].replace("_copy", "_acpc") + ".gz"
        os.rename(dsts[0]+".gz", petToEstimate)

        pet4070 = dsts[1].replace("_copy", "_acpc") + ".gz"
        os.rename(dsts[1]+".gz", pet4070)

        pet5070 = dsts[2].replace("_copy", "_acpc") + ".gz"
        os.rename(dsts[2]+".gz", pet5070)


    for pet, _dir, params in zip(
            [pet4070, pet5070, pet4070],
            ["pet", "centiloid", "tmp"],
            [petParams, centiloidParams, tmpParams],
            ):

        output = os.path.join(_dir, add_suffix(pet, "space-anat")).replace("_acpc", "")

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

