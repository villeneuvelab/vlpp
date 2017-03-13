# -*- coding: utf-8 -*-
"""
"""


from lib.utils import WorkflowManager


class Smoothing(WorkflowManager):

    def __init__(self, config, name):
        WorkflowManager.__init__(self, config, name)

    def generate(self):
        if self.kind == 'UCD':
            self._wf = self._UCD()
        else:
            self._wf = self._UCD()
            #self.implement_error()

    def connect(self, main_wf):
        preparation = main_wf.get_node('Preparation')

        main_wf.connect([
            (preparation, self._wf, [('petconvert.out_file', 'smooth.in_file')]),
            ])


    def _UCD(self):
        from nipype.interfaces.fsl.maths import MeanImage
        from nipype.interfaces.fsl.utils import Smooth
        from nipype.pipeline.engine import Node, Workflow

        smooth = Node(Smooth(), 'smooth')
        smooth.iterables = ('fwhm', self.config['fwhm'])

        meanimage = Node(MeanImage(), 'meanimage')

        wf = Workflow(self.name)

        wf.connect([
            (smooth, meanimage, [('smoothed_file', 'in_file')]),
            ])

        #wf.add_nodes([
            #smooth,
            #])

        return wf
