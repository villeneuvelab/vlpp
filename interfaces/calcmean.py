# -*- coding: utf-8 -*-


import nibabel as nb
import numpy as np
from os.path import abspath as opa

from nipype.interfaces.base import BaseInterface, \
    BaseInterfaceInputSpec, traits, File, TraitedSpec, isdefined
from nipype.utils.filemanip import split_filename


class CalcMeanInputSpec(BaseInterfaceInputSpec):
    in_files = traits.List(
            File(exists=True),
            desc='List of frames',
            mandatory=True)
    durations = traits.List(
            traits.Float,
            desc='Durations of each frames to compute weighted average',
            mandatory=False)
    indices = traits.List(
            traits.Int,
            desc='List of indices of frames to mean',
            mandatory=False)
    tag = traits.String(mandatory=True)
    mean_method = traits.Enum(
            'UCD_spm', 'UCD_python',
            desc="Method to average frames ('UCD_spm'[default], 'UCD_python')")


class CalcMeanOutputSpec(TraitedSpec):
    out_file = File(exists=True, desc="Mean volume")


class CalcMean(BaseInterface):
    input_spec = CalcMeanInputSpec
    output_spec = CalcMeanOutputSpec

    def _run_interface(self, runtime):
        frames = np.array(self.inputs.in_files)
        durations = np.array(self.inputs.durations)
        ind = self.inputs.indices
        tag = self.inputs.tag
        mean_method = self.inputs.mean_method

        if isdefined(self.inputs.indices):
            frames = frames[ind]
            if isdefined(self.inputs.durations):
                durations = durations[ind]

        _, base, ext = split_filename(frames[0])
        self._out_file = opa('{}_mean{}{}'.format(base, tag, ext))
        make_mean(frames, self._out_file, mean_method)

        return runtime

    def _list_outputs(self):
        outputs = self._outputs().get()
        outputs['out_file'] = self._out_file
        return outputs


def make_mean(niftilist, target, mean_method):
    if mean_method == 'UCD_spm':
        make_mean_spm(niftilist, target)
    elif mean_method == 'UCD_python':
        make_mean_python(niftilist, target)
    else:
        msg = "'{}' is not implemented for the calcmean interface"
        print(msg.format(mean_method))


def make_mean_spm(niftilist, target, durations=None):
    """
    Given a list of nifti files, generates a mean image
    """
    n_images = len(niftilist)
    affine = nb.load(niftilist[0]).get_affine()
    header = nb.load(niftilist[0]).get_header()
    shape =  nb.load(niftilist[0]).get_shape()
    newdat = np.zeros([n_images] + list(shape))
    for i, item in enumerate(niftilist):
        newdat[i] += nb.load(item).get_data().copy()
    tmp = np.round(newdat*10000)/10000
    rtmp = np.prod(tmp, 0)
    rtmp2 = np.prod((newdat + np.absolute(newdat)), 0)
    ind = (rtmp > 0) & (rtmp2 > 0)
    ind4d = np.tile(ind, [n_images,1,1,1])
    newdatMask = np.ma.MaskedArray(newdat, ~ind4d)
    newdatMean = np.mean(newdatMask, 0, durations)
    newimg = nb.Nifti1Image(newdatMean, affine, header)
    newimg.to_filename(target)
    return target


def make_mean_python(niftilist, target, durations=None):
    """
    Given a list of nifti files, generates a mean image
    """
    n_images = len(niftilist)
    affine = nb.load(niftilist[0]).get_affine()
    header = nb.load(niftilist[0]).get_header()
    shape =  nb.load(niftilist[0]).get_shape()
    newdat = np.zeros([n_images] + list(shape))
    for i, item in enumerate(niftilist):
        newdat[i] += nb.load(item).get_data().copy()
    newdat = np.mean(newdat, 0, durations)
    newdat = np.nan_to_num(newdat)
    newimg = nb.Nifti1Image(newdat, affine, header)
    newimg.to_filename(target)
    return target

