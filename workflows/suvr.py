# -*- coding: utf-8 -*-
"""
"""


from lib.utils import WorkflowManager


class Suvr(WorkflowManager):

    def __init__(self, config, name):
        WorkflowManager.__init__(self, config, name)

    def generate(self):
        if self.kind == '50to70':
            self._wf = self._suvr50to70()
        else:
            self.implement_error()

    def connect(self, main_wf):
        fssource = main_wf.get_node('fssource')
        preparation = main_wf.get_node('Preparation')
        t1registration = main_wf.get_node('T1registration')
        datasink = main_wf.get_node('datasink')

        main_wf.connect([
            (fssource, self._wf, [
                ('aseg', 'pickatlas.atlas'),
                ('aseg', 'segstats.segmentation_file'),
                ]),
            (t1registration, self._wf,
                [('coregister.coregistered_source', 'suvrcalc.in_file')]),
            (self._wf, datasink, [
                ('pickatlas.mask_file', 'SUVr.@mask'),
                ('suvrcalc.out_file', 'SUVr.@suvr'),
                ('segstats.summary_file', 'SUVr.@stats'),
                ]),
            ])


    def _suvr50to70(self):
        from interfaces.suvrcalc import SuvrCalc
        from nipype.algorithms.misc import PickAtlas
        from nipype.interfaces.freesurfer.model import SegStats
        from nipype.interfaces.utility import Function
        from nipype.pipeline.engine import MapNode, Node, Workflow

        '''
        pickatlas = MapNode(
                PickAtlas(
                    labels=tuple(self.config['labels'].values()),
                    #output_file=list(self.config['labels'].keys()),
                    ),
                name='pickatlas',
                #iterfield=['labels', 'output_file'])
                iterfield=['labels'])
        '''
        pickatlas = Node(
                PickAtlas(labels=self.config['labels']['cerebellar']),
                name='pickatlas')

        suvrcalc = Node(
                SuvrCalc(),
                name='suvrcalc',
                )#iterfield=['refmask_file'])

        segstats = Node(
                SegStats(
                    #color_table_file = '',
                    default_color_table = True,
                    exclude_id = 0,
                    ),
                name='segstats',
                )#iterfied=['in_file'])

        # Workflow
        wf = Workflow(self.name)

        wf.connect([
            (pickatlas, suvrcalc, [('mask_file', 'refmask_file')]),
            (suvrcalc, segstats, [('out_file', 'in_file')]),
            ])

        return wf

