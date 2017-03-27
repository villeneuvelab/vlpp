# -*- coding: utf-8 -*-
"""
"""


from ..lib.utils import WorkflowManager


class Preparation(WorkflowManager):

    def __init__(self, config, name):
        WorkflowManager.__init__(self, config, name)
        self.infields = [
                "frametimes",
                "petframes",
                "anat",
                "atlas",
                ]
        self.outfields = [
                "pet",
                "anat",
                "atlas",
                ]
        self.setnodes()

    def generate(self):
        if self.kind == 'default':
            self._wf = self.default()
        else:
            self.error()

    def default(self):
        #from ..interfaces.sortframes import SortFrames
        from ..interfaces.mnc2nii import Mnc2Nii
        #from nipype.algorithms.misc import Gunzip
        from nipype.interfaces.freesurfer.preprocess import MRIConvert
        from nipype.pipeline.engine import Node, Workflow
        from nipype.interfaces.utility import Function


        def ext(in_file):
            from nipype.utils.filemanip import split_filename
            _, base, ext = split_filename(in_file)
            return ext

        def select(in_files):
            for f in in_files:
                if "aparc+aseg.mgz" in f:
                    return f

        #sortframes = Node(SortFrames(origin='UCD'), 'sortframes')

        asegFile = Node(Function(
                        input_names=['in_files'], output_names=['out_file'],
                        function=select), name='asegFile')

        #mnc2nii = Node(Mnc2Nii(), 'mnc2nii')
        petconvert = Node(Mnc2Nii(), 'petconvert')
        #petconvert = Node(MRIConvert(out_type='niigz'), 'petconvert')
        #petconvert = Node(Gunzip(), 'petconvert')
        t1convert = Node(MRIConvert(out_type='niigz'), 't1convert')
        asegconvert = Node(MRIConvert(out_type='niigz'), 'asegconvert')

        wf = Workflow(self.name)

        wf.connect([
            #(self.inputnode, sortframes, [('frametimes', 'in_file')]),
            (self.inputnode, petconvert, [('petframes', 'in_file')]),
            (self.inputnode, t1convert, [('anat', 'in_file')]),
            (self.inputnode, asegFile, [('atlas', 'in_files')]),
            (asegFile, asegconvert, [('out_file', 'in_file')]),
            #(mnc2nii, petconvert, [('out_file', 'in_file')]),
            (petconvert, self.outputnode, [('out_file', 'pet')]),
            (t1convert, self.outputnode, [('out_file', 'anat')]),
            (asegconvert, self.outputnode, [('out_file', 'atlas')]),
            ])

        return wf
