# -*- coding: utf-8 -*-
"""
"""


from ..lib.utils import WorkflowManager


class Anatreg(WorkflowManager):

    def __init__(self, config, name):
        self.infields = [
                "pet",
                "anat",
                ]
        self.outfields = [
                "pet",
                "petnii",
                "anatnii",
                ]
        WorkflowManager.__init__(self, config, name)

    def generate(self):
        if self.kind == 'spm':
            self._wf = self.spm()
        elif self.kind == 'fsl':
            #self._wf = self._fsl()
            self.error()
        else:
            self.error()

    def spm(self):
        from nipype.algorithms.misc import Gunzip
        from nipype.interfaces.fsl.maths import MathsCommand
        from nipype.interfaces.spm import Coregister
        from nipype.pipeline.engine import Node, Workflow

        anatnii = Node(Gunzip(), 'anatnii')
        petnii = Node(Gunzip(), 'petnii')

        petgz = Node(MathsCommand(output_type='NIFTI_GZ'), 'petgz')

        coregister= Node(
                Coregister(**self.config['coregister_param']), 'coregister')

        wf = Workflow(self.name)

        wf.connect([
            (self.inputnode, anatnii, [('anat', 'in_file')]),
            (anatnii, coregister, [('out_file', 'target')]),
            (anatnii, self.outputnode, [('out_file', 'anatnii')]),
            (self.inputnode, petnii, [('pet', 'in_file')]),
            (petnii, coregister, [('out_file', 'source')]),
            (coregister, petgz, [('coregistered_source', 'in_file')]),
            (petgz, self.outputnode, [('out_file', 'pet')]),
            (coregister, self.outputnode, [('coregistered_source', 'petnii')]),
            ])

        return wf

    def fsl(self):
        pass
