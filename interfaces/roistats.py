# -*- coding: utf-8 -*-


import nibabel as nb
import numpy as np
from os.path import abspath as opa
import os
import csv

from nipype.interfaces.base import BaseInterface, \
    BaseInterfaceInputSpec, traits, File, TraitedSpec
from nipype.utils.filemanip import split_filename


class RoiStatsInputSpec(BaseInterfaceInputSpec):
    in_file = File(exists=True, mandatory=True, desc='Volume file')
    seg_file = File(exists=True, mandatory=True, desc='Segmentation file')
    labels = traits.Dict(desc='')

class RoiStatsOutputSpec(TraitedSpec):
    out_file = File(exists=True, desc='Stats inside the ROI [mean, std, min, max, range]')

class RoiStats(BaseInterface):
    input_spec = RoiStatsInputSpec
    output_spec = RoiStatsOutputSpec

    def _run_interface(self, runtime):
        in_file = self.inputs.in_file
        seg_file = self.inputs.seg_file
        labels = self.inputs.labels

        volData = nb.load(in_file).get_data()
        segData = nb.load(seg_file).get_data()

        stats = [['StructName', 'mean', 'std', 'min', 'max', 'range']]

        for structName, values in labels.items():
            mask = np.zeros_like(segData)
            for value in values:
                mask[segData==value] = 1

            data = np.ma.masked_where(mask==0, volData, True)

            stats.append([
                    structName,
                    float(data.mean()),
                    float(data.std()),
                    float(data.min()),
                    float(data.max()),
                    float(data.max()-data.min()),
                    ])

        self._out_file = opa('nav_stats.csv')

        print(stats)
        with open(self._out_file, 'wt') as csvfile:
            w = csv.writer(csvfile)#, delimiter=',', quotechar='"')
            w.writerows(stats)

        return runtime

    def _list_outputs(self):
        outputs = self._outputs().get()
        outputs['out_file'] = self._out_file
        return outputs

