# -*- coding: utf-8 -*-


import numpy as np

from nipype.interfaces.base import BaseInterface, \
    BaseInterfaceInputSpec, traits, File, TraitedSpec
from nipype.utils.filemanip import split_filename


class SortFramesInputSpec(BaseInterfaceInputSpec):
    frametimes = File(
            exists=True,
            desc='Path of the file with frame times informations',
            mandatory=True)
    origin = traits.Enum(
            'UCD', 'centiloid',
            mandatory=True,
            desc="origin of the framing file")


class SortFramesOutputSpec(TraitedSpec):
    ind5 = traits.List(
            traits.Int, desc='List of first 5 minutes frames')
    indnot5 = traits.List(
            traits.Int, desc='All frames except first 5 minutes')
    ind50to70 = traits.List(
            traits.Int, desc='List of 50 to 70 minutes frames')
    durations = traits.List(
            traits.Float, desc='Durations of each frames')


class SortFrames(BaseInterface):
    input_spec = SortFramesInputSpec
    output_spec = SortFramesOutputSpec

    def _run_interface(self, runtime):
        frametimes = self.inputs.frametimes
        origin = self.inputs.origin
        data = import_framing(frametimes, origin)

        startTime = data[:,1]
        duration = data[:,2]
        stopTime = data[:,3]

        self._ind5 = np.where(stopTime <= 5.*60)[0]
        self._indnot5 = np.where(stopTime > 5.*60)[0]
        #self.ind20 = stopTime <= 20.*60
        self._ind50to70 = np.where((startTime>=50.*60) & (stopTime<=70.*60))[0]
        self._durations = duration

        return runtime

    def _list_outputs(self):
        outputs = self._outputs().get()
        outputs['ind5'] = self._ind5.tolist()
        outputs['indnot5'] = self._indnot5.tolist()
        outputs['ind50to70'] = self._ind50to70.tolist()
        outputs['durations'] = self._durations.tolist()
        return outputs


def import_framing(framingPath, origin):
    frametimes = None

    if origin == 'UCD':
        frametimes = np.genfromtxt(framingPath, delimiter=',', dtype=float)
        frametimes = np.round(frametimes[1:,:])

    elif origin == 'centiloid':
        pass

    else:
        pass

    return frametimes

