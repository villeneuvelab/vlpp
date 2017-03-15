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
                #('segstats.summary_file', 'Segstats.@stats'),
                #('roistats.out_file', 'Segstats.@roistats'),
                ('mergeNode.stats', 'Segstats.@stats'),
                ]),
            ])


    def _suvr50to70(self):
        from interfaces.roistats import RoiStats
        from nipype.algorithms.misc import PickAtlas
        from nipype.interfaces.freesurfer.model import SegStats
        from nipype.interfaces.utility import Function
        from nipype.pipeline.engine import MapNode, JoinNode, Node, Workflow

        def merge(roistats, stats):
            from os.path import abspath as opa
            import pandas
            output = opa('merged_stats.csv')
            roiData = pandas.read_csv(roistats)
            data = pandas.read_csv(
                    stats, delim_whitespace=True, comment="#",
                    usecols=[4, 5, 6, 7, 8, 9], names=roiData.columns.values)
            mergeData = roiData.append(data)
            mergeData.to_csv(output)
            return output


        roistats = Node(RoiStats(labels=self.config['labels']), 'roistats')

        segstats = Node(
                SegStats(
                    #color_table_file = '',
                    default_color_table = True,
                    exclude_id = 0,
                    ),
                name='segstats',
                )#iterfied=['in_file'])

        mergeNode = Node(Function(
                    input_names=['roistats', 'stats'], output_names=['stats'],
                    function=merge), 'mergeNode')

        # Workflow
        wf = Workflow(self.name)

        #wf.add_nodes([
            #segstats,
            #roistats,
            #])
        wf.connect([
            (roistats, mergeNode, [('out_file', 'roistats')]),
            (segstats, mergeNode, [('summary_file', 'stats')]),
            ])

        return wf

