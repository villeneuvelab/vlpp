# -*- coding: utf-8 -*-
"""
"""


from ..lib.utils import WorkflowManager


class Pvc(WorkflowManager):

    def __init__(self, config, name):
        self.infields = [
                "pet",
                "seg",
                ]
        self.outfields = [
                "petpvc",
                ]
        WorkflowManager.__init__(self, config, name)

    def generate(self):
        if self.kind == 'default':
            self._wf = self.default()
        else:
            self.error()

    def default(self):
        from nipype.interfaces.petpvc import PETPVC
        #from nipype.interfaces.fsl.utils import Smooth
        from nipype.pipeline.engine import Node, Workflow

        petpvc = Node(PETPVC(**self.config["petpvc"]), 'petpvc')

        wf = Workflow(self.name)

        wf.connect([
            (self.inputnode, petpvc, [('pet', 'in_file')]),
            (self.inputnode, petpvc, [('seg', 'mask_file')]),
            (petpvc, self.outputnode, [('out_file', 'petpvc')]),
            ])

        return wf
