# -*- coding: utf-8 -*-
"""
"""


from lib.utils import WorkflowManager


class T1registration(WorkflowManager):

    def __init__(self, config, name):
        WorkflowManager.__init__(self, config, name)

    def generate(self):
        if self.kind == 'spm':
            self._wf = self._spm()
        elif self.kind == 'fsl':
            #self._wf = self._fsl()
            self.implement_error()
        else:
            self.implement_error()

    def connect(self, main_wf):
        preparation = main_wf.get_node('Preparation')
        realign = main_wf.get_node('Realign')
        datasink = main_wf.get_node('datasink')

        main_wf.connect([
            (preparation, self._wf,
                [('mriconvert.out_file', 'coregister.target')]),
            (realign, self._wf, [
                ('calcmean50to70.out_file', 'coregister.source'),
                ('tile_data.realigned_files', 'coregister.apply_to_files'),
                ]),
            (self._wf, datasink, [
                ('coregister.coregistered_source', 't1registration'),
                ('coregister.coregistered_files', 'co_file'),
                ]),
            ])


    def _spm(self):
        #from nipype.algorithms.misc import Gunzip
        from nipype.interfaces.spm import Coregister
        from nipype.pipeline.engine import Node, Workflow

        #gunzip = Node(Gunzip(), 'gunzip')

        coregister= Node(Coregister(**self.config['coregister_param']),
                                    'coregister')

        wf = Workflow(self.name)

        wf.add_nodes([coregister])

        #wf.connect([
            #(gunzip, coregister, [('out_file', 'target')]),
            #])

        return wf


    def _fsl(self):
        pass

#ToRefactor
'''
        inputnode = pe.Node(
                niu.IdentityInterface(fields=['anat', 'pet']),
                'inputnode')

        estimate = pe.Node(fsl.FLIRT(), 'flirt')
        estimate.inputs.dof = 6
        estimate.inputs.uses_qform = True

        invt = pe.Node(fsl.ConvertXFM(), 'invt')
        invt.inputs.invert_xfm = True

        register = pe.Node(fsl.FLIRT(), 'register')
        register.inputs.apply_xfm = True

        wf = pe.Workflow('registration')

        wf.connect([
            (inputnode, estimate, [
                ('pet', 'in_file'),
                ('anat', 'reference')]),
            (estimate, invt, [('out_matrix_file', 'in_file')])
            ])

        if target == 'anat':
            wf.connect([
                (inputnode, register, [
                    ('pet', 'in_file'),
                    ('anat', 'reference')]),
                (estimate, register, [('out_matrix_file', 'in_matrix_file')])
                ])
        elif target == 'pet':
            wf.connect([
                (inputnode, register, [
                    ('anat', 'in_file'),
                    ('pet', 'reference')]),
                (invt, register, [('out_file', 'in_matrix_file')])
                ])
        else:
            print "config['target'] should be 'anat' or 'pet'"

        # Define the outputnode
        outputnode = pe.Node(
                niu.IdentityInterface(fields=[
                    'pet2anat_matrix',
                    'anat2pet_matrix',
                    'register_file']),
                'outputnode')

        wf.connect([
            (estimate, outputnode, [('out_matrix_file', 'pet2anat_matrix')]),
            (invt, outputnode, [('out_file', 'anat2pet_matrix')]),
            (register, outputnode, [('out_file', 'register_file')])
            ])
        return wf
'''
