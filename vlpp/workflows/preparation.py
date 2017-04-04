# -*- coding: utf-8 -*-
"""
"""


from ..lib.utils import WorkflowManager


class Preparation(WorkflowManager):

    def __init__(self, config, name):
        self.infields = [
                "frametimes",
                "pet",
                "anat",
                "atlas",
                ]
        self.outfields = [
                "pet",
                "anat",
                "atlas",
                ]
        WorkflowManager.__init__(self, config, name)

    def generate(self):
        if self.kind == 'default':
            self._wf = self.default()
        else:
            self.error()

    def default(self):
        from ..interfaces.mnc2nii import Mnc2Nii
        #from ..interfaces.sortframes import SortFrames
        from nipype.interfaces.fsl.maths import MathsCommand
        from nipype.interfaces.freesurfer.preprocess import MRIConvert
        from nipype.pipeline.engine import Node, Workflow
        from nipype.interfaces.utility import Function


        # PET conversion
        petconvert = Node(Mnc2Nii(), 'petconvert')
        petgz = Node(MathsCommand(output_type='NIFTI_GZ'), 'petgz')

        # Frames
        #sortframes = Node(SortFrames(origin='UCD'), 'sortframes')

        # Anat
        anatconvert = Node(MRIConvert(out_type='niigz'), 'anatconvert')

        # Atlas
        def _selectatlas(in_files):
            if isinstance(in_files, list):
                for f in in_files:
                    if "aparc+aseg.mgz" in f:
                        return f
            else:
                return in_files

        selectatlas = Node(Function(
                        input_names=['in_files'], output_names=['out_file'],
                        function=_selectatlas), name='selectatlas')

        atlasconvert = Node(MRIConvert(out_type='niigz'), 'atlasconvert')

        # Workflow
        wf = Workflow(self.name)

        if self.config["ext"] == "mnc":
            wf.connect([
                (self.inputnode, petconvert, [('pet', 'in_file')]),
                (petconvert, petgz, [('out_file', 'in_file')]),
                (petgz, self.outputnode, [('out_file', 'pet')]),
                ])
        elif self.config["ext"] == "nii.gz":
            wf.connect([
                (self.inputnode, self.outputnode, [('pet', 'pet')]),
                ])

        wf.connect([
            #(self.inputnode, sortframes, [('frametimes', 'in_file')]),
            (self.inputnode, anatconvert, [('anat', 'in_file')]),
            (anatconvert, self.outputnode, [('out_file', 'anat')]),
            (self.inputnode, selectatlas, [('atlas', 'in_files')]),
            (selectatlas, atlasconvert, [('out_file', 'in_file')]),
            (atlasconvert, self.outputnode, [('out_file', 'atlas')]),
            ])

        """
        def ext(in_file):
            from nipype.utils.filemanip import split_filename
            _, base, ext = split_filename(in_file)
            return ext
        """

        return wf
