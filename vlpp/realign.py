# -*- coding: utf-8 -*-


import nibabel
import os
import sys
from glob import glob
from .utils import add_suffix, run_shell, run_matlab


class Realign(object):


    def __init__(self, petPath, dataset, ignore):
        self.dataset = dataset
        self.ignore = ignore

        self.petPath = petPath
        self.pet = nibabel.load(petPath)

        #trim images
        self.trim4070 = add_suffix(petPath, "trim-4070")
        self.trim5070 = add_suffix(petPath, "trim-5070")

        #output
        self.petToEstimate = add_suffix(petPath, "tmp-estimate")
        self.pet4070 = add_suffix(petPath, "time-4070")
        self.pet5070 = add_suffix(petPath, "time-5070")

        #directory
        os.mkdir("transform")

        #transform
        self.petRealignTmp = os.path.join(
                "transform", add_suffix(self.trim4070, "tmp-realign4d"))
        self.realignParams = os.path.join(
                "transform", "realign_parameters.txt")


    def run(self):
        if self.petIs4d:
            """
            If the input pet is 4d:
              - trim the data to extract frames of interest, 40to70
              - realign the data
            """
            self._trimPetTo4070()

            print(self.ignore)
            if self.ignore == "true":
                """
                If the user ignore the realign:
                    - Tmean and smooth the image to estimate coregistration
                    - Tmean the image to register
                    - trim to centiloid and Tmean de image to register
                """
                self._prepareOutputFrom(self.trim4070)

            else:
                self._realign()

        else:
            """
            If the input pet is 3d:
              - we only smooth the image to estimate coregistration
            """
            self._tmean_and_smooth(self.petInput, self.petToEstimate)
            os.symlink(self.petPath, self.pet4070)
            os.symlink(self.petPath, self.pet5070)


    @property
    def petIs4d(self):
        shape = self.pet.shape
        if len(shape) == 3:
            return False
        elif len(shape) == 4:
            return True
        else:
            sys.exit()


    def _trimPetTo4070(self):
        if self.dataset == "DIAN":
            self._trim_DIAN()

        elif self.dataset == "PAD":
            os.symlink(self.petPath, self.trim4070)

        else:
            messages = [
                "process: realign",
                "  {} name unknown".format(self.dataset),
                "  frames are consider 40min to 70min",
                ]
            for m in messages:
                print(m)
            os.symlink(self.petPath, self.trim4070)


    def _trim_DIAN(self):
        """
        For 4070 images:
          6 volumes  -> keep it like that
          32 volumes -> keep last 5 volumes
          33 volumes -> keep last 6 volumes
          other      -> exit the pipeline
        """

        nbVol = self.pet.shape[-1]
        if nbVol == 33:
            cmd = "fslroi {0} {1} 27 -1".format(self.petPath, self.trim4070)
            run_shell(cmd)

        elif nbVol == 32:
            cmd = "fslroi {0} {1} 27 -1".format(self.petPath, self.trim4070)
            run_shell(cmd)

        elif nbVol == 6:
            os.symlink(self.petPath, self.trim4070)

        else:
            sys.exit()


    def _tmean_and_smooth(self, input, output, smooth=True):
        # Temporal average
        #cmd = "fslmaths {0} -nan -Tmean tmp.nii.gz".format(input)
        cmd = "fslmaths {0} -Tmean tmp.nii.gz"
        run_shell(cmd.format(input))

        # Smoothing
        if smooth:
            #cmd="fslmaths tmp.nii.gz -kernel gauss 2.548 -fmean -nan {0}"
            cmd="fslmaths tmp.nii.gz -kernel gauss 2.548 -fmean {0}"
            run_shell(cmd.format(output))
        else:
            run_shell("cp tmp.nii.gz {0}".format(output))


    def _prepareOutputFrom(self, orig):
        self._tmean_and_smooth(orig, self.petToEstimate)
        self._tmean_and_smooth(orig, self.pet4070, False)

        cmd = "fslroi {0} {1} 2 -1"
        run_shell(cmd.format(orig, self.trim5070))
        self._tmean_and_smooth(self.trim5070, self.pet5070, False)


    def _realign(self):
        #split nifti
        run_shell("fslsplit {}".format(self.trim4070))
        volList = glob("vol*.nii.gz")
        run_shell("gzip -d {}".format(" ".join(volList)))

        #run matlab realign
        tags = {
                "files": sorted(glob("vol*.nii"))
                }
        run_matlab("realign.m", tags, "realign.m")

        #merge realigned files
        rvolList = " ".join(glob("rvol*"))
        run_shell("fslmerge -t {0} {1}".format(self.petRealignTmp, rvolList))
        os.symlink("../rp_vol0000.txt", self.realignParams)

        self._prepareOutputFrom(self.petRealignTmp)
