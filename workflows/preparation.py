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
        fssource = main_wf.get_node('fssource')

        main_wf.connect([
            (petfiles, self._wf, [('frametimes', 'sortframes.frametimes')]),
            (fssource, self._wf, [('T1', 'mriconvert.in_file')]),
            ])


    def _UCD(self):
        from interfaces.sortframes import SortFrames
        from nipype.interfaces.freesurfer.preprocess import MRIConvert
        from nipype.pipeline.engine import Node, Workflow

        def ext(in_file):
            from nipype.utils.filemanip import split_filename
            _, base, ext = split_filename(in_file)
            return ext

        sortframes = Node(SortFrames(origin='UCD'), 'sortframes')

        mriconvert = Node(MRIConvert(out_type='nii'), 'mriconvert')

        wf = Workflow(self.name)

        wf.add_nodes([
            sortframes,
            mriconvert,
            ])

        return wf
