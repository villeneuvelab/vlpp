# -*- coding: utf-8 -*-
"""
"""


from ..lib.utils import WorkflowManager


class Suvr(WorkflowManager):

    def __init__(self, config, name):
        self.infields = [
                "atlas",
                "pet",
                ]
        self.outfields = [
                "suvr",
                "mask",
                ]
        WorkflowManager.__init__(self, config, name)

    def generate(self):
        if self.kind == 'default':
            self._wf = self.default()
        else:
            self.error()

    def default(self):
        from ..interfaces.suvrcalc import SuvrCalc
        from nipype.algorithms.misc import PickAtlas
        from nipype.pipeline.engine import Node, Workflow

        pickatlas = Node(PickAtlas(), name='pickatlas')
        iterables = []
        for key, value in self.config['pickatlas']['labels'].items():
            iterables.append(value)
        pickatlas.iterables = ("labels", iterables)

        suvrcalc = Node(SuvrCalc(), name='suvrcalc')

        # Workflow
        wf = Workflow(self.name)

        wf.connect([
            (self.inputnode, pickatlas, [('atlas', 'atlas')]),
            (self.inputnode, suvrcalc, [('pet', 'in_file')]),
            (pickatlas, suvrcalc, [('mask_file', 'refmask_file')]),
            (pickatlas, self.outputnode, [('mask_file', 'mask')]),
            (suvrcalc, self.outputnode, [('out_file', 'suvr')]),
            ])

        return wf

