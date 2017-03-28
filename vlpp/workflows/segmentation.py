# -*- coding: utf-8 -*-
"""
"""


from ..lib.utils import WorkflowManager


class Segmentation(WorkflowManager):

    def __init__(self, config, name):
        self.infields = [
                "anat",
                "anatnii",
                ]
        self.outfields = [
                "seg",
                ]
        WorkflowManager.__init__(self, config, name)

    def generate(self):
        if self.kind == 'spm':
            self._wf = self.spm()
        else:
            self.error()


    def spm(self):
        from nipype.interfaces.spm import NewSegment
        from nipype.interfaces.fsl import Merge
        from nipype.pipeline.engine import Node, Workflow

        def listoflist2list(native_class_images):
            return [_[0] for _ in native_class_images]

        newsegment = Node(NewSegment(**self.config['newsegment']), 'newsegment')
        merge = Node(Merge(dimension='t', output_type='NIFTI_GZ'), 'merge')

        wf = Workflow(self.name)

        wf.connect([
            (self.inputnode, newsegment, [('anatnii', 'channel_files')]),
            (newsegment, merge,
                [(('native_class_images', listoflist2list), 'in_files')]),
            (merge, self.outputnode, [('merged_file', 'seg')]),
            ])

        return wf
