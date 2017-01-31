# -*- coding: utf-8 -*-
"""
"""


from lib.utils import WorkflowManager


class Preparation(WorkflowManager):

    def __init__(self, config, name):
        WorkflowManager.__init__(self, config, name)

    def generate(self):
        if self.kind == 'UCD':
            self._wf = self._UCD()
        else:
            self.implement_error()

    def connect(self, main_wf):
        petfiles = main_wf.get_node('petfiles')

        main_wf.connect([
            (petfiles, self._wf, [
                ('frametimes', 'sortframes.frametimes'),
                #('petframes', 'convert.petframes'),
                ]),
            ])


    def _UCD(self):
        from interfaces.sortframes import SortFrames
        #from interfaces.convert import Convert
        from nipype.pipeline.engine import Node, Workflow

        sortframes = Node(SortFrames(origin='UCD'), 'sortframes')
        #TODO Check nifti or dcm format
        #convert = Node(Convert(image_format=config['image_format'], 'convert')

        wf = Workflow(self.name)
        wf.add_nodes([
            sortframes,
            #convert,
            ])

        return wf
