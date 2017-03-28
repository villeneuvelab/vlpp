# -*- coding: utf-8 -*-
"""
"""


from ..lib.utils import WorkflowManager


class Statsrois(WorkflowManager):

    def __init__(self, config, name):
        self.infields = [
                "atlas",
                "suvr",
                ]
        self.outfields = [
                "stats",
                ]
        WorkflowManager.__init__(self, config, name)

    def generate(self):
        if self.kind == 'default':
            self._wf = self.default()
        else:
            self.error()

    def default(self):
        from ..interfaces.userstats import Userstats
        from nipype.algorithms.misc import PickAtlas
        from nipype.interfaces.freesurfer.model import SegStats
        from nipype.interfaces.utility import Function
        from nipype.pipeline.engine import Node, Workflow

        def merge(stats, userstats, suvr_file):
            from os.path import abspath as opa
            from nipype.utils.filemanip import split_filename
            import pandas

            _, base, ext = split_filename(suvr_file)
            output = opa('{}_stats.csv'.format(base))
            userData = pandas.read_csv(userstats)
            data = pandas.read_csv(
                    stats, delim_whitespace=True, comment="#",
                    usecols=[4, 5, 6, 7, 8, 9], names=userData.columns.values)
            mergeData = userData.append(data)
            mergeData.to_csv(output)
            return output

        segstats = Node(
                SegStats(default_color_table = True, exclude_id = 0),
                'segstats')

        userstats = Node(Userstats(), 'userstats')
        userstats.inputs.user_labels = self.config['userstats_labels']

        mergestats = Node(Function(
                    input_names=['stats', 'userstats', 'suvr_file'],
                    output_names=['out_file'],
                    function=merge), 'mergestats')

        # Workflow
        wf = Workflow(self.name)

        wf.connect([
            (self.inputnode, segstats, [('atlas', 'segmentation_file')]),
            (self.inputnode, userstats, [('atlas', 'atlas_file')]),
            (self.inputnode, segstats, [('suvr', 'in_file')]),
            (self.inputnode, userstats, [('suvr', 'in_file')]),
            (segstats, mergestats, [('summary_file', 'stats')]),
            (userstats, mergestats, [('out_file', 'userstats')]),
            (self.inputnode, mergestats, [('suvr', 'suvr_file')]),
            (mergestats, self.outputnode, [('out_file', 'stats')]),
            ])

        return wf
