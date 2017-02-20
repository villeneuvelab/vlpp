# -*- coding: utf-8 -*-
"""
"""


from lib.utils import WorkflowManager


class Segmentation(WorkflowManager):

    def __init__(self, config, name):
        WorkflowManager.__init__(self, config, name)

    def generate(self):
        if self.kind == 'spm':
            self._wf = self._spm()
        elif self.kind == 'fsl':
            #self._wf = self._fsl()
            self.implement_error()
        else:
            self.implement_error()

    def connect(self, main_wf):
        preparation = main_wf.get_node('Preparation')
        datasink = main_wf.get_node('datasink')

        main_wf.connect([
            (preparation, self._wf,
                [('mriconvert.out_file', 'newsegment.channel_files')]),
            (self._wf, datasink,
                [('merge.merged_file', 'segmentation')]),
            ])


    def _spm(self):
        from nipype.interfaces.spm import NewSegment
        from nipype.interfaces.fsl import Merge
        from nipype.pipeline.engine import Node, Workflow

        def listoflist2list(native_class_images):
            return [_[0] for _ in native_class_images]

        newsegment = Node(NewSegment(**self.config['newsegment']), 'newsegment')
        merge = Node(Merge(dimension='t', output_type='NIFTI_GZ'), 'merge')

        wf = Workflow(self.name)

        wf.connect([
            (newsegment, merge,
                [(('native_class_images', listoflist2list), 'in_files')]),
            ])

        return wf
