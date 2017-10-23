#!/usr/bin/env python
# -*- coding: utf-8 -*-


import glob
import nibabel
import os
import sys
from subprocess import call
from jinja2 import Environment, FileSystemLoader


class Realign(object):

    def __init__(self):
        os.mkdir("transform")

        self.status = "${params.realign}"
        self.petInput = "${pet}"
        self.petImg = nibabel.load(self.petInput)
        self.petToEstimate = "${participant}_tmp-toEstimate${suffix.pet}"
        self.petToRegister = "${participant}_tmp-toRegister${suffix.pet}"
        self.petCentiloid = "${participant}_tmp-centiloid${suffix.pet}"

        self.trim4070 = "${participant}_trim4070.nii.gz"
        self.trim5070 = "${participant}_trim5070.nii.gz"

        self.petRealignTmp = "transform/${participant}_tmp-realign${suffix.pet}"

    @property
    def petIs4d(self):
        shape = self.petImg.shape
        if len(shape) == 3:
            return False
        elif len(shape) == 4:
            return True
        else:
            sys.exit()

    def mean_and_smooth(self, input, output, smooth=True):
        # spatial average
        cmd = "fslmaths {0} -nan -Tmean tmp.nii.gz".format(input)
        call(cmd, shell=True)
        # smoothing
        if smooth:
            cmd="fslmaths tmp.nii.gz -kernel gauss 2.548 -fmean -nan {0}".format(
                    output)
            call(cmd, shell=True)
        else:
            call("cp tmp.nii.gz {0}".format(output), shell=True)

    def trimPetTo4070(self):
        if "${params.study}" == "DIAN":
            self.trim_DIAN()
        elif "${params.study}" == "PAD":
            os.symlink(self.petInput, self.trim4070)
        else:
            print("${params.study}: not known, consider it is 40 to 70")
            os.symlink(self.petInput, self.trim4070)

    def trim_DIAN(self):
        """
        For 4070 images:
          6 volumes  -> keep it like that
          32 volumes -> keep last 5 volumes
          33 volumes -> keep last 6 volumes
          other      -> exit the pipeline
        """
        nbVol = self.petImg.shape[-1]
        if nbVol == 33:
            cmd = "fslroi {0} {1} 27 -1".format(self.petInput, self.trim4070)
            call(cmd, shell=True)
        elif nbVol == 32:
            cmd = "fslroi {0} {1} 27 -1".format(self.petInput, self.trim4070)
            call(cmd, shell=True)
        elif nbVol == 6:
            os.symlink(self.petInput, self.trim4070)
        else:
            sys.exit()

    def realign(self):
        call("fslsplit {}".format(self.trim4070), shell=True)
        call("gzip -d vol*.nii.gz", shell=True)

        tags = {
                "files": sorted(glob.glob("vol*.nii"))
                }
        j2_env = Environment(
                loader=FileSystemLoader(os.path.join("${baseDir}", "templates")),
                trim_blocks=True)
        j2_env.get_template('realign.m').stream(**tags).dump("realign.m")

        call("matlab -nodisplay < realign.m", shell=True)
        call("fslmerge -t {0} rvol*".format(self.petRealignTmp), shell=True)
        self.mean_and_smooth(self.petRealignTmp, self.petToEstimate)
        self.mean_and_smooth(self.petRealignTmp, self.petToRegister, False)
        cmd = "fslroi {0} {1} 2 -1".format(self.petRealignTmp, self.trim5070)
        call(cmd, shell=True)
        self.mean_and_smooth(self.trim5070, self.petCentiloid, False)
        #call("fslmaths {0} -nan {0}".format(self.output), shell=True)
        #call("fslmaths {0} -Tmean {1}".format(self.petToEst), shell=True)
        os.symlink("rp_vol0000.txt", "transform/realign_parameters.txt")

    def run(self):
        if self.petIs4d:
            """
            If the input pet is 4d:
              - trim the data to extract frames of interest, 40to70
              - realign the data
            """
            self.trimPetTo4070()
            if self.status == "ignore":
                """
                If the user ignore the realign:
                    - Tmean and smooth the image to estimate coregistration
                    - Tmean the image to register
                    - trim to centiloid and Tmean de image to register
                """
                self.mean_and_smooth(self.trim4070, self.petToEstimate)
                self.mean_and_smooth(self.trim4070, self.petToToRegister, False)
                cmd = "fslroi {0} {1} 2 -1".format(self.trim4070, self.trim5070)
                call(cmd, shell=True)
                self.mean_and_smooth(self.trim5070, self.petCentiloid, False)
            else:
                print("GO REALIGN")
                self.realign()
        else:
            """
            If the input pet is 3d:
              - we only smooth the image to estimate coregistration
            """
            self.mean_and_smooth(self.petInput, self.petToEstimate)
            os.symlink(self.petInput, self.petToRegister)
            os.symlink(self.petInput, self.petCentiloid)


realign = Realign()
realign.run()
