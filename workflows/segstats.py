# -*- coding: utf-8 -*-
"""
"""


from lib.utils import WorkflowManager


class Segstats(WorkflowManager):

    def __init__(self, config, name):
        WorkflowManager.__init__(self, config, name)

    def generate(self):
        if self.kind == 'default':
            self._wf = self._suvr50to70()
        else:
            self.implement_error()

    def connect(self, main_wf):
        fssource = main_wf.get_node('fssource')
        preparation = main_wf.get_node('Preparation')
        suvr = main_wf.get_node('Suvr')
        datasink = main_wf.get_node('datasink')

        main_wf.connect([
            (preparation, self._wf, [
                ('asegconvert.out_file', 'segstats.segmentation_file'),
                ('asegconvert.out_file', 'roistats.seg_file'),
                ]),
            (suvr, self._wf, [
                ('suvrcalc.out_file', 'segstats.in_file'),
                ('suvrcalc.out_file', 'roistats.in_file'),
                ]),
            (self._wf, datasink, [
                ('segstats.summary_file', 'Segstats.@stats'),
                ('roistats.out_file', 'Segstats.@roistats'),
                ]),
            ])


    def _suvr50to70(self):
        from interfaces.roistats import RoiStats
        from nipype.algorithms.misc import PickAtlas
        from nipype.interfaces.freesurfer.model import SegStats
        from nipype.interfaces.utility import Function
        from nipype.pipeline.engine import MapNode, JoinNode, Node, Workflow

        '''
        pickatlas = Node(PickAtlas(), name='pickatlas')
        pickatlas.iterables = ('labels', list(labels.values()))
                #iterfield=['labels', 'output_file'])
                iterfield=['labels'])
                    labels=tuple(labels.values()),
        pickatlas = Node(
                PickAtlas(labels=self.config['labels']['cerebellar']),
                name='pickatlas')
        '''

        roistats = Node(RoiStats(labels=self.config['labels']), 'roistats')

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

        wf.add_nodes([
            segstats,
            roistats,
            ])
        #wf.connect([
            #(pickatlas, roistats, [('mask_file', 'roi_file')]),
            #(roistats, csv, [('stat', 'stats')]),
            #])

        return wf

