# -*- coding: utf-8 -*-
"""
"""


from lib.utils import WorkflowManager


class Qa(WorkflowManager):

    def __init__(self, config, name):
        WorkflowManager.__init__(self, config, name)

    def generate(self):
        if self.kind == 'classic':
            self._wf = self._qawf()
        else:
            self.implement_error()

    def connect(self, main_wf):
        preparation = main_wf.get_node('Preparation')
        datasink = main_wf.get_node('datasink')

        main_wf.connect([
            (preparation, self._wf, [
                ('asegconvert.out_file', 'brainmask.in_file'),
                ]),
            (self._wf, datasink, [('brainmask.out_file', 'qa.@brainmask')]),
            ])

    def _qawf(self):
        from nipype.interfaces.fsl.maths import UnaryMaths
        from nipype.pipeline.engine import Node, Workflow

        brainmask = Node(UnaryMaths(operation='bin'), 'brainmask')

        wf = Workflow(self.name)

        wf.add_nodes([
            brainmask,
            ])

        return wf

