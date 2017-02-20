# -*- coding: utf-8 -*-
"""
"""


from lib.utils import WorkflowManager


class Realign(WorkflowManager):

    def __init__(self, config, name):
        WorkflowManager.__init__(self, config, name)

    def generate(self):
        if self.kind == 'UCD':
            self._wf = self._UCD()
        else:
            self.implement_error()

    def connect(self, main_wf):
        petfiles = main_wf.get_node('petfiles')
        preparation = main_wf.get_node('Preparation')
        datasink = main_wf.get_node('datasink')

        main_wf.connect([
            (petfiles, self._wf, [('petframes', 'gunzip.in_file')]),
            (preparation, self._wf, [
                ('sortframes.ind5', 'calcmean5.indices'),
                ('sortframes.durations', 'calcmean5.durations'),
                ('sortframes.ind5', 'merge_mean.indices'),
                ('sortframes.ind50to70', 'calcmean50to70.indices'),
                ('sortframes.durations', 'calcmean50to70.durations'),
                ]),
            (self._wf, datasink, [
                ('calcmean5.out_file', 'realign.@mean5'),
                ('calcmean50to70.out_file', 'realign.@mean50to70'),
                ('tile_data.realigned_files', 'realign.@realigned_files'),
                ('tile_data.realignment_parameters', 'realign.@tparameters'),
                ('realign.realignment_parameters', 'realign.@parameters'),
                ]),
            ])


    def _UCD(self):
        from interfaces.calcmean import CalcMean
        from nipype.algorithms.misc import Gunzip
        from nipype.interfaces.spm import Realign
        from nipype.interfaces.utility import Function
        from nipype.pipeline.engine import MapNode, Node, Workflow

        def merge(in_files, indices, mean):
            import numpy as np
            frames = np.array(in_files)
            frames = np.delete(frames, indices)
            frames = np.insert(frames, 0, mean)
            return frames.tolist(), len(indices)

        def tile(in_files, realigned_files, realignment_parameters, length):
            import numpy as np
            from nipype.utils.filemanip import split_filename
            from os.path import abspath as opa

            output_rf = in_files[:length] + realigned_files[1:]

            rp = np.loadtxt(realignment_parameters)
            output_rp = np.concatenate((np.tile(rp[0,:], [length,1]), rp[1:,:]))
            _, base, ext = split_filename(realignment_parameters)
            output_rp_name = opa('{}_tile{}'.format(base, ext))
            np.savetxt(output_rp_name, output_rp, fmt='%.7e')
            return output_rf, output_rp_name

        gunzip = MapNode(Gunzip(), name='gunzip', iterfield=['in_file'])

        calcmean5 = Node(CalcMean(**self.config['calcmean_param']), 'calcmean5')
        calcmean5.inputs.tag= '5'

        merge_mean = Node(Function(input_names=['in_files', 'indices', 'mean'],
                                  output_names=['out_files', 'length'],
                                  function=merge), name='merge_mean')

        realign = Node(Realign(**self.config['realign_param']), 'realign')

        tile_data = Node(Function(input_names=['in_files',
                                               'realigned_files',
                                               'realignment_parameters',
                                               'length'],
                                  output_names=['realigned_files',
                                                'realignment_parameters'],
                                  function=tile), name='tile_data')

        calcmean50to70 = Node(
                CalcMean(**self.config['calcmean_param']), 'calcmean50to70')
        calcmean50to70.inputs.tag= '50to70'

        wf = Workflow(self.name)

        wf.connect([
            (gunzip, calcmean5, [('out_file', 'in_files')]),
            (gunzip, merge_mean, [('out_file', 'in_files')]),
            (calcmean5, merge_mean, [('out_file', 'mean')]),
            (merge_mean, realign, [('out_files', 'in_files')]),
            (gunzip, tile_data, [('out_file', 'in_files')]),
            (realign, tile_data, [
                ('realigned_files', 'realigned_files'),
                ('realignment_parameters', 'realignment_parameters'),
                ]),
            (merge_mean, tile_data, [('length', 'length')]),
            (tile_data, calcmean50to70, [('realigned_files', 'in_files')]),
            ])

        return wf
