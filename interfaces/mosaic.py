# -*- coding: utf-8 -*-


#import nibabel as nb
#import numpy as np
from lib import mosaic
from os.path import abspath as opa

from nipype.interfaces.base import BaseInterface, \
    BaseInterfaceInputSpec, File, TraitedSpec, isdefined, traits
    #BaseInterfaceInputSpec, traits, File, TraitedSpec
from nipype.utils.filemanip import split_filename


class MosaicInputSpec(BaseInterfaceInputSpec):
    in_file = File(exists=True, mandatory=True, desc='3d Image')
    mask_file = File(exists=True, mandatory=False, desc='Mask Image')
    contour_file = File(exists=True, mandatory=False, desc='Contour Image')
    overlay_file = File(exists=True, mandatory=False, desc='Overlay Image')
    cmap = traits.Str(desc='matplotlib cmap')
    postfix = traits.Str(desc='')

class MosaicOutputSpec(TraitedSpec):
    mosaic_file = File(exists=True, desc='Mosaic image')
    #html_file = File(exists=True, desc='HTML brainsprite page')
    tags = traits.Dict(desc='brainsprite tags')

class Mosaic(BaseInterface):
    input_spec = MosaicInputSpec
    output_spec = MosaicOutputSpec

    def _run_interface(self, runtime):
        in_file = self.inputs.in_file
        mask_file = self.inputs.mask_file
        contour_file = self.inputs.contour_file
        overlay_file = self.inputs.overlay_file
        cmap = self.inputs.cmap
        if isdefined(self.inputs.postfix):
            postfix = "_{}".format(self.inputs.postfix)
        else:
            postfix = ""

        _, name, _ = split_filename(in_file)
        self._mosaic_file_path = opa('{}_mosaic{}.png'.format(name, postfix))
        self._html_file_path = opa('{}_mosaic{}.html'.format(name, postfix))

        result = mosaic.Mosaic(in_file)
        if isdefined(mask_file): result.mask = mask_file
        if isdefined(contour_file): result.contour = contour_file
        if isdefined(overlay_file): result.overlay = overlay_file
        if isdefined(cmap): result.cmap = cmap
        self._tags = result.save(self._mosaic_file_path)
        #mosaic.create_index(tags, self._html_file_path)

        return runtime

    def _list_outputs(self):
        outputs = self._outputs().get()
        outputs['mosaic_file'] = self._mosaic_file_path
        #outputs['html_file'] = self._html_file_path
        outputs['tags'] = self._tags
        return outputs


