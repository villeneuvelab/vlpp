# -*- coding: utf-8 -*-


import nibabel as nb
import numpy as np
from os.path import abspath as opa

from nipype.interfaces.base import BaseInterface, \
    BaseInterfaceInputSpec, traits, File, TraitedSpec
from nipype.utils.filemanip import split_filename


class SuvrCalcInputSpec(BaseInterfaceInputSpec):
    in_file = File(exists=True, mandatory=True, desc='PET image')
    refmask_file = File(exists=True, mandatory=True, desc='Reference mask file')

class SuvrCalcOutputSpec(TraitedSpec):
    out_file = File(exists=True, desc='Standardized Uptake Value Ratio (SUVR)')

class SuvrCalc(BaseInterface):
    input_spec = SuvrCalcInputSpec
    output_spec = SuvrCalcOutputSpec

    def _run_interface(self, runtime):
        in_file = self.inputs.in_file
        refmask_file = self.inputs.refmask_file

        image = nb.load(in_file)
        affine = image.get_affine()
        petData = image.get_data()
        refmaskData = nb.load(refmask_file).get_data()

        _, name, ext = split_filename(in_file)
        self._out_file_path = opa('{}_suvr{}'.format(name, ext))

        refData = np.ma.masked_where(refmaskData==0, petData, True)
        suvrData = petData / refData.mean()

        nb.save(nb.Nifti1Image(suvrData, affine), self._out_file_path)

        return runtime

    def _list_outputs(self):
        outputs = self._outputs().get()
        outputs['out_file'] = self._out_file_path
        return outputs

