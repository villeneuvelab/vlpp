# -*- coding: utf-8 -*-


import nibabel as nb
import numpy as np
from os.path import abspath as opa
import csv

from nipype.interfaces.base import BaseInterface, \
    BaseInterfaceInputSpec, traits, File, TraitedSpec


class InputSpec(BaseInterfaceInputSpec):
    in_file = File(exists=True, mandatory=True, desc='Volume file')
    atlas_file = File(exists=True, mandatory=True, desc='Atlas file')
    user_labels = traits.Dict(desc='')

class OutputSpec(TraitedSpec):
    out_file = File(exists=True, desc='csv file, header: [mean, std, min, max, range]')

class Userstats(BaseInterface):
    input_spec = InputSpec
    output_spec = OutputSpec

    def _run_interface(self, runtime):
        in_file = self.inputs.in_file
        atlas_file = self.inputs.atlas_file
        user_labels = self.inputs.user_labels

        volData = nb.load(in_file).get_data()
        atlasData = nb.load(atlas_file).get_data()

        stats = [['StructName', 'mean', 'std', 'min', 'max', 'range']]

        for structName, values in user_labels.items():
            mask = np.zeros_like(atlasData)
            for value in values:
                mask[atlasData==value] = 1

            data = np.ma.masked_where(mask==0, volData, True)

            stats.append([
                    structName,
                    float(data.mean()),
                    float(data.std()),
                    float(data.min()),
                    float(data.max()),
                    float(data.max()-data.min()),
                    ])

        self._out_file = opa('stats_user_labels.csv')
        with open(self._out_file, 'wt') as csvfile:
            w = csv.writer(csvfile)#, delimiter=',', quotechar='"')
            w.writerows(stats)

        return runtime

    def _list_outputs(self):
        outputs = self._outputs().get()
        outputs['out_file'] = self._out_file
        return outputs

