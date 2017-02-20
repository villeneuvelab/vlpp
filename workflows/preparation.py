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
            (fssource, self._wf, [('T1', 't1convert.in_file')]),
            (fssource, self._wf, [('aseg', 'asegconvert.in_file')]),
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

        t1convert = Node(MRIConvert(out_type='nii'), 't1convert')
        asegconvert = Node(MRIConvert(out_type='niigz'), 'asegconvert')

        wf = Workflow(self.name)

        wf.add_nodes([
            sortframes,
            t1convert,
            asegconvert,
            ])

        return wf
