# -*- coding: utf-8 -*-
"""
"""


import os
from ..lib.utils import WorkflowManager


class Mosaics(WorkflowManager):

    def __init__(self, config, name):
        self.infields = [
                "anat",
                "atlas",
                "petreg",
                "mask",
                "suvr",
                ]
        self.outfields = [
                "files",
                "tags",
                ]
        WorkflowManager.__init__(self, config, name)

    def generate(self):
        if self.kind == 'default':
            self._wf = self.default()
        else:
            self.implement_error()


    def default(self):
        from ..interfaces.mosaic import Mosaic
        from nipype.interfaces.utility import Merge
        from nipype.pipeline.engine import Node, Workflow

        wf = Workflow(self.name)
        mosaics = []

        # T1
        suffix = 't1'
        m = Node(Mosaic(**self.config[suffix]), 'mosaic{}'.format(suffix))
        m.inputs.suffix = suffix
        wf.connect([
            (self.inputnode, m, [('anat', 'in_file')]),
            ])
        mosaics.append(m)

        # T1 segmentation
        suffix = 't1seg'
        m = Node(Mosaic(**self.config[suffix]), 'mosaic{}'.format(suffix))
        m.inputs.suffix = suffix
        wf.connect([
            (self.inputnode, m, [
                ('anat', 'in_file'),
                ('atlas', 'overlay_file'),
                ]),
            ])
        mosaics.append(m)

        # PET
        suffix = 'pet'
        m = Node(Mosaic(**self.config[suffix]), 'mosaic{}'.format(suffix))
        m.inputs.suffix = suffix
        wf.connect([
            (self.inputnode, m, [('petreg', 'in_file')]),
            ])
        mosaics.append(m)

        # PET segmentation
        suffix = 'petseg'
        m = Node(Mosaic(**self.config[suffix]), 'mosaic{}'.format(suffix))
        m.inputs.suffix = suffix
        wf.connect([
            (self.inputnode, m, [
                ('petreg', 'in_file'),
                ('atlas', 'overlay_file'),
                ]),
            ])
        mosaics.append(m)

        # SUVr
        suffix = 'suvr'
        m = Node(Mosaic(**self.config[suffix]), 'mosaic{}'.format(suffix))
        m.inputs.suffix = suffix
        wf.connect([
            (self.inputnode, m, [
                ('suvr', 'in_file'),
                ('mask', 'contour_file'),
                ]),
            ])
        mosaics.append(m)

        # Merge Nodes
        mergefiles = Node(Merge(len(mosaics)), "mergefiles")
        mergetags = Node(Merge(len(mosaics)), "mergetags")
        for n, m in enumerate(mosaics):
            wf.connect(m, 'out_file', mergefiles, 'in{}'.format(n))
            wf.connect(m, 'tag', mergetags, 'in{}'.format(n))

        wf.connect(mergefiles, 'out', self.outputnode, 'files')
        wf.connect(mergetags, 'out', self.outputnode, 'tags')

        return wf

