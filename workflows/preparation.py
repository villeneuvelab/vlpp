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
            self._wf = self._UCD()
            #self.implement_error()

    def connect(self, main_wf):
        petfiles = main_wf.get_node('petfiles')
        fssource = main_wf.get_node('fssource')

        main_wf.connect([
            #(petfiles, self._wf, [('frametimes', 'sortframes.frametimes')]),
            (petfiles, self._wf, [('petframes', 'petconvert.in_file')]),
            (fssource, self._wf, [('T1', 't1convert.in_file')]),
            (fssource, self._wf, [('aparc_aseg', 'asegFile.in_files')]),
            ])


    def _UCD(self):
        from interfaces.sortframes import SortFrames
        from nipype.interfaces.freesurfer.preprocess import MRIConvert
        from nipype.pipeline.engine import Node, Workflow
        from nipype.interfaces.utility import Function

        def ext(in_file):
            from nipype.utils.filemanip import split_filename
            _, base, ext = split_filename(in_file)
            return ext

        def select(in_files):
            for i in in_files:
                if "aparc+aseg.mgz" in i:
                    return i

        #sortframes = Node(SortFrames(origin='UCD'), 'sortframes')

        asegFile = Node(Function(
                        input_names=['in_files'],
                        output_names=['out_file'],
                        function=select), name='asegFile')

        petconvert = Node(MRIConvert(out_type='niigz'), 'petconvert')
        t1convert = Node(MRIConvert(out_type='nii'), 't1convert')
        asegconvert = Node(MRIConvert(out_type='niigz'), 'asegconvert')

        wf = Workflow(self.name)

        wf.add_nodes([
            #sortframes,
            petconvert,
            t1convert,
            asegconvert,
            ])

        wf.connect([
            (asegFile, asegconvert, [('out_file', 'in_file')]),
            ])

        return wf
