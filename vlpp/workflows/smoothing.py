# -*- coding: utf-8 -*-
"""
"""


from ..lib.utils import WorkflowManager


class Smoothing(WorkflowManager):

    def __init__(self, config, name):
        self.infields = [
                "pet",
                ]
        self.outfields = [
                "pet",
                ]
        WorkflowManager.__init__(self, config, name)

    def generate(self):
        if self.kind == 'default':
            self._wf = self.default()
        else:
            self.error()

    def default(self):
        from nipype.interfaces.fsl.maths import MeanImage
        from nipype.interfaces.fsl.utils import Smooth
        from nipype.pipeline.engine import Node, Workflow

        smooth = Node(Smooth(), 'smooth')
        smooth.iterables = ('fwhm', self.config['fwhm'])

        meanimage = Node(MeanImage(), 'meanimage')

        wf = Workflow(self.name)

        wf.connect([
            (self.inputnode, smooth, [('pet', 'in_file')]),
            (smooth, meanimage, [('smoothed_file', 'in_file')]),
            (meanimage, self.outputnode, [('out_file', 'pet')]),
            ])

        return wf
