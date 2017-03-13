# -*- coding: utf-8 -*-
"""
"""


import os
from lib.utils import WorkflowManager


class Qa(WorkflowManager):

    def __init__(self, config, name):
        WorkflowManager.__init__(self, config, name)

    def generate(self):
        if self.kind == 'classic':
            #self._wf = self._qawf()
            self._wf = self._qamosaic()
        else:
            self.implement_error()

    def connect(self, main_wf):
        infosource = main_wf.get_node('infosource')
        preparation = main_wf.get_node('Preparation')
        smoothing = main_wf.get_node('Smoothing')
        t1registration = main_wf.get_node('T1registration')
        suvr = main_wf.get_node('Suvr')
        datasink = main_wf.get_node('datasink')

        main_wf.connect([
            (infosource, self._wf, [
                ('subject_id', 'dashboard.subject_id'),
                ('subject_id', 'merge.subject_id'),
                ]),
            (preparation, self._wf, [
                #('asegconvert.out_file', 'brainmask.in_file'),
                #('asegconvert.out_file', 'rgb.input_image'),
                ('t1convert.out_file', 'mosaicT1.in_file'),
                ('t1convert.out_file', 'mosaicT1seg.in_file'),
                ('asegconvert.out_file', 'mosaicT1seg.overlay_file'),
                ('asegconvert.out_file', 'mosaicPetseg.overlay_file'),
                ]),
            #(smoothing, self._wf, [('meanimage.out_file', 'mosaicPet.in_file')]),
            (t1registration, self._wf, [
                ('coregister.coregistered_source', 'mosaicPet.in_file'),
                #('coregister.coregistered_source', 'mosaicPetwm.in_file'),
                ('coregister.coregistered_source', 'mosaicPetseg.in_file'),
                ]),
            (suvr, self._wf, [
                ('suvrcalc.out_file', 'mosaicSuvr.in_file'),
                ('pickatlas.mask_file', 'mosaicSuvr.contour_file'),
                ]),
            (self._wf, datasink, [
                ('assets.bcss', 'Qa.assets.@bcss'),
                ('assets.keencss', 'Qa.assets.@keencss'),
                ('assets.jquery', 'Qa.assets.@jquery'),
                ('assets.bjs', 'Qa.assets.@bjs'),
                ('assets.holder', 'Qa.assets.@holder'),
                ('assets.keen', 'Qa.assets.@keen'),
                ('assets.meta', 'Qa.assets.@meta'),
                ('assets.bs', 'Qa.assets.@bs'),
                ('dashboard.html_file', 'Qa.@dashboard'),
                ('mosaicT1.mosaic_file', 'Qa.@mosaicT1'),
                ('mosaicT1seg.mosaic_file', 'Qa.@mosaicT1seg'),
                ('mosaicPet.mosaic_file', 'Qa.@mosaicPet'),
                #('mosaicPetwm.mosaic_file', 'Qa.@mosaicPetwm'),
                ('mosaicPetseg.mosaic_file', 'Qa.@mosaicPetseg'),
                ('mosaicSuvr.mosaic_file', 'Qa.@mosaicSuvr'),
                ]),
            ])

    def _qamosaic(self):
        from interfaces.dashboard import Dashboard
        from interfaces.mosaic import Mosaic
        from nipype.interfaces.io import SelectFiles
        from nipype.interfaces.utility import Function
        from nipype.pipeline.engine import Node, Workflow

        def test(
                tagsT1,
                tagsT1seg,
                tagsPet,
                #tagsPetwm,
                tagsPetseg,
                tagsSuvr,
                subject_id):
            import os
            tagsT1.update({
                'title': 'T1',
                'notes': 'Freesufer T1 in native space',
                'canvas_id': 'canvas_t1',
                'sprite': 'sprite_t1',
                })
            tagsT1seg.update({
                'title': 'T1 and aparc+aseg',
                'notes': 'Freesufer T1 in native space with aparc+aseg as overlay',
                'canvas_id': 'canvas_t1seg',
                'sprite': 'sprite_t1seg',
                })
            tagsPet.update({
                'title': 'PET',
                'notes': 'PET image in freesurfer native space',
                'canvas_id': 'canvas_pet',
                'sprite': 'sprite_pet',
                })
            #tagsPetwm.update({
                #'title': 'PET and white matter segmentation',
                #'notes': 'PET image in freesurfer native space with white matter contour',
                #'canvas_id': 'canvas_petwm',
                #'sprite': 'sprite_petwm',
                #})
            tagsPetseg.update({
                'title': 'PET and aparc+aseg',
                'notes': 'PET image in freesurfer native space with aparc+aseg as overlay',
                'canvas_id': 'canvas_petseg',
                'sprite': 'sprite_petseg',
                })
            tagsSuvr.update({
                'title': 'SUVr',
                'notes': 'SUVr image in freesurfer native space with brainstem contour',
                'canvas_id': 'canvas_suvr',
                'sprite': 'sprite_suvr',
                })
            return {
                    'mosaics': [
                        tagsT1,
                        tagsT1seg,
                        tagsPet,
                        #tagsPetwm,
                        tagsPetseg,
                        tagsSuvr
                        ],
                    'subject_id': subject_id,
                    }

        assets = Node(
                SelectFiles({
            'bcss': "dashboards/assets/lib/bootstrap/dist/css/bootstrap.min.css",
            'keencss': "dashboards/assets/css/keen-dashboards.css",
            'jquery': "dashboards/assets/lib/jquery/dist/jquery.min.js",
            'bjs': "dashboards/assets/lib/bootstrap/dist/js/bootstrap.min.js",
            'holder': "dashboards/assets/lib/holderjs/holder.js",
            'keen': "dashboards/assets/lib/keen-js/dist/keen.min.js",
            'meta': "dashboards/assets/js/meta.js",
            'bs': 'brainsprite.js/brainsprite.min.js',
            }),
            'assets')
        assets.inputs.base_directory = '/home/chris/local'

        mosaicT1 = Node(Mosaic(cmap='gray'), 'mosaicT1')
        mosaicT1seg = Node(Mosaic(cmap='gray', postfix='T1seg'), 'mosaicT1seg')
        mosaicPet = Node(Mosaic(), 'mosaicPet')
        #mosaicPetwm = Node(Mosaic(), 'mosaicPetwm')
        mosaicPetseg = Node(Mosaic(cmap='gray', postfix='Petseg'), 'mosaicPetseg')
        mosaicSuvr = Node(Mosaic(), 'mosaicSuvr')

        merge = Node(Function(
                        input_names=[
                            'tagsT1',
                            'tagsT1seg',
                            'tagsPet',
                            #'tagsPetwm',
                            'tagsPetseg',
                            'tagsSuvr',
                            'subject_id'],
                        output_names=['tags'],
                        function=test), name='merge')

        dashboard = Node(Dashboard(), 'dashboard')

        wf = Workflow(self.name)

        wf.add_nodes([
            assets,
            #mosaicT1,
            #mosaicPet,
            #mosaicSuvr,
            ])
        wf.connect([
            (mosaicT1, merge, [('tags', 'tagsT1')]),
            (mosaicT1seg, merge, [('tags', 'tagsT1seg')]),
            (mosaicPet, merge, [('tags', 'tagsPet')]),
            #(mosaicPetwm, merge, [('tags', 'tagsPetwm')]),
            (mosaicPetseg, merge, [('tags', 'tagsPetseg')]),
            (mosaicSuvr, merge, [('tags', 'tagsSuvr')]),
            (merge, dashboard, [('tags', 'tags')]),
            #(suvr_wf, rgb, [('pickatlas.mask_file', 'input_image')]),
            #(suvr_wf, mosaic, [('suvrcalc.out_file', 'input_image')]),
            #(brainmask, rgb, [('out_file', 'mask_image')]),
            #(brainmask, mosaic, [('out_file', 'mask_image')]),
            #(rgb, mosaic, [('output_image', 'rgb_image')]),
            ])

        return wf


    def _qawf(self):
        from nipype.interfaces.fsl.maths import UnaryMaths
        from nipype.interfaces.ants.visualization import \
                ConvertScalarImageToRGB, CreateTiledMosaic
        from nipype.pipeline.engine import Node, Workflow

        brainmask = Node(UnaryMaths(operation='bin'), 'brainmask')
        brainmask.inputs.out_file = 'brainmask.nii.gz'

        rgb = Node(ConvertScalarImageToRGB(**self.config['rgb']), 'rgb')
        #rgb.inputs.custom_color_map_file = os.path.join(
                #os.getenv('FREESURFER_HOME'), 'FreeSurferColorLUT.txt')
        #toad/templates/lookup_tables/FreeSurferColorLUT_ItkSnap.txt

        mosaic = Node(CreateTiledMosaic(**self.config['mosaic']), 'mosaic')
        #mosaic.inputs.input_image = '/home/chris/Projets/Sylvia/data/derivatives/pipeline_working_dir/PIPELINENAME/SUVR/_subject_id_B12-303/suvrcalc/rrB12-303_PIB_frame0030_mean_suvr.nii'

        wf = Workflow(self.name)

        #wf.add_nodes([brainmask, rgb])
        wf.connect([
            #(suvr_wf, rgb, [('pickatlas.mask_file', 'input_image')]),
            #(suvr_wf, mosaic, [('suvrcalc.out_file', 'input_image')]),
            (brainmask, rgb, [('out_file', 'mask_image')]),
            (brainmask, mosaic, [('out_file', 'mask_image')]),
            (rgb, mosaic, [('output_image', 'rgb_image')]),
            ])

        return wf
