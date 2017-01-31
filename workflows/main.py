# -*- coding: utf-8 -*-


import os
import sys

from nipype import config
from nipype import logging

import nipype.interfaces.io as nio
import nipype.interfaces.utility as niu
import nipype.pipeline.engine as pe

from lib import utils


def main_wf(config_dict):

    # Usefull variables
    output_dir = config_dict['arguments']['output_dir']
    working_dir = config_dict['arguments']['working_dir']
    user_debug = config_dict['arguments']['debug']
    subject_list = [config_dict['arguments']['subject_id']]
    input_dir = config_dict['arguments']['input_dir']
    templates = config_dict['selectfiles']['petfiles']
    fssource_subject_id = config_dict['selectfiles']['freesurfer']


    # Directories
    for directory in [output_dir, working_dir]:
        if not os.path.exists(directory):
            os.makedirs(directory)


    # Nipype configuration
    config_dict['logging']['log_directory'] = output_dir
    config.update_config(config_dict)
    if user_debug:
        config.enable_debug_mode()
    logging.update_logging(config)


    # Main workflow
    main_wf = pe.Workflow(name=utils.__PIPELINENAME__)
    main_wf.base_dir = working_dir


    # Infosource
    infields = ['subject_id']
    infosource = pe.Node(niu.IdentityInterface(fields=infields), 'infosource')
    infosource.iterables = [
            ('subject_id', subject_list),
            ]


    # PET Files
    petfiles = pe.Node(nio.SelectFiles(templates), 'petfiles')
    petfiles.inputs.base_directory = input_dir
    petfiles.inputs.sort_filelist = True
    #petfiles.inputs.raise_on_empty = False


    # Freesurfer source
    fssource = pe.Node(nio.FreeSurferSource(), 'fssource')
    fssource.inputs.subjects_dir = input_dir
    fssource.inputs.subject_id = fssource_subject_id


    # Datasink
    datasink = pe.Node(nio.DataSink(), 'datasink')
    datasink.inputs.base_directory = output_dir
    #TODO
    substitutions = [
            ('_subject_id_', '')
            ]
    #datasink.inputs.substitutions = substitutions


    # General connections
    main_wf.connect([
        (infosource, petfiles, [[_] *2 for _ in infields]),
        (infosource, fssource, [[_] *2 for _ in infields]),
        #(infosource, datasink, [('subject_id', 'container')]),
        ])
    main_wf.add_nodes([datasink])


    # Worflows


    ## Preparation
    from workflows.preparation import Preparation
    preparation = Preparation(config_dict['preparation'], 'Preparation')
    preparation.implement(main_wf)

    '''
    # Realign
    from workflows.realign import Realign
    realign = Realign(config_dict['realign'], 'Realign')
    realign.generate()
    realign.connect(main_wf)
    print main_wf.list_nodes_names()

    # T1 registration
    t1registrationName = config_dict['t1registration']['name']

    if t1registrationName == 'spm':
        #import
        from workflows.t1registration import t1registration_spm
        t1registration = t1registration_spm(config_dict['t1registration'])
        #connect
        main_wf.connect([
            (selectfiles, t1registration, [('anat', 'gunzip.in_file')]),
            (wfd['realign'], t1registration,
                [('calcmean.out_file', 'coregister.source')]),
            (t1registration, datasink, [
                ('coregister.coregistered_files',
                    't1registration.@coregistered_files'),
                ('coregister.coregistered_source',
                    't1registration.@coregistered_source'),
                ]),
            ])

    elif t1registrationName == 'fsl':
        pass
        #TODO return registration_fsl(config)

    else:
        msg = "'{}' is not implemented for the t1registration workflow"
        print msg.format(t1registrationName)



    # Template Registration
    tplregistrationName = config_dict['tplregistration']['name']

    if tplregistrationName == 'spm':
        pass
        #import
        #coregistertemplate = pe.Node(
                #spm.Coregister(**config_dict['tplregistration']['coregister__param']),
                #'coregistertemplate')

    else:
        msg = "'{}' is not implemented for the t1registration workflow"
        print msg.format(tplregistrationName)


    # Segmentation
    segmentationName = config_dict['segmentation']['name']

    if segmentationName == 'spm':
        #import
        from workflows.segmentation import segmentation_spm
        segmentation = segmentation_spm(config_dict['segmentation'])
        #connect
        main_wf.connect([
            (t1registration, segmentation,
                [('gunzip.out_file', 'newsegment.channel_files')]),
            (segmentation, datasink,
                [('merge.merged_file', 'segmentation')]),
            ])

    else:
        msg = "'{}' is not implemented for the segmentation workflow"
        print msg.format(segmentationName)


    # SUVR
    if config_dict['suvr']['cerebellar']:
        #import
        from workflows.suvr import suvr_cerebellar
        suvr_wf = suvr_cerebellar()
        #connect
        main_wf.connect([
            (selectfiles, suvr_wf, [
                ('aparcaseg', 'pickatlas.atlas'),
                ('aparcaseg', 'segstats.segmentation_file'),
                ]),
            (t1registration, suvr_wf,
                [('coregister.coregistered_source', 'suvrcalc.in_file')]),
            (suvr_wf, datasink, [
                ('pickatlas.mask_file', 'suvr.@cerebellarmask'),
                ('suvrcalc.out_file', 'suvr.@suvr'),
                ('segstats.summary_file', 'suvr.@segstats'),
                ]),
            ])

    if config_dict['suvr']['whitematter']:
        pass


    # Simple brainmask for visu
    from nipype.interfaces.fsl.maths import UnaryMaths
    brainmask = pe.Node(UnaryMaths(operation='bin'), 'brainmask')
    main_wf.connect([
        (selectfiles, brainmask, [('aparcaseg', 'in_file')]),
        (brainmask, datasink, [('out_file', 'brainmask')]),
        ])


    # Visualization
    #from workflows.visualization import mosaic_wf
    #mosaic_cereb = mosaic_wf()

    from nipype.pipeline.engine import Node, Workflow
    from nipype.interfaces.ants.visualization import \
            ConvertScalarImageToRGB, CreateTiledMosaic


    rgb = pe.Node(ConvertScalarImageToRGB(), 'rgb')
    rgb.inputs.colormap = 'jet' #colormap
    rgb.inputs.dimension = 3 #dimension
    rgb.inputs.minimum_input = 0 #minimum_input
    rgb.inputs.maximum_input = 2 #maximum_input
    #rgb.inputs.input_image = '/home/chris/Projets/Sylvia/data/derivatives/pipeline_working_dir/PIPELINENAME/SUVR/_subject_id_B12-303/pickatlas/B12-303_aparc_aseg_mask.nii.gz'
    #rgb.inputs.custom_color_map_file = '/home/chris/local/toad/templates/lookup_tables/FreeSurferColorLUT_ItkSnap.txt'

    mosaic = pe.Node(CreateTiledMosaic(), 'createTiledMosaic')
    mosaic.inputs.alpha_value = 0.5
    mosaic.inputs.flip_slice = '1x1'
    mosaic.inputs.pad_or_crop = 'mask'
    mosaic.inputs.output_image = 'output.jpg'
    #mosaic.inputs.input_image = '/home/chris/Projets/Sylvia/data/derivatives/pipeline_working_dir/PIPELINENAME/SUVR/_subject_id_B12-303/suvrcalc/rrB12-303_PIB_frame0030_mean_suvr.nii'
    #createTiledMosaic.mask_image = ''

    """
    main_wf.connect([
        (suvr_wf, rgb, [('pickatlas.mask_file', 'input_image')]),
        (suvr_wf, mosaic, [('suvrcalc.out_file', 'input_image')]),
        (brainmask, mosaic, [('out_file', 'mask_image')]),
        (rgb, mosaic, [('output_image', 'rgb_image')]),
        (mosaic, datasink, [('output_image', 'mosaic')]),
        ])
    """

    #PVC
    from interfaces.petpvc import PETPVC
    petpvc = pe.Node(
            PETPVC(**config_dict["pvc"]["params"]),
            'petpvc')
    main_wf.connect([
        (t1registration, petpvc, [('coregister.coregistered_source', 'in_file')]),
        (segmentation, petpvc, [('merge.merged_file', 'mask_file')]),
        ])

    #SUVR-PVC
    suvrpvc_wf = suvr_wf.clone(name='SUVR_PVC')

    main_wf.connect([
        (selectfiles, suvrpvc_wf, [
            ('aparcaseg', 'pickatlas.atlas'),
            ('aparcaseg', 'segstats.segmentation_file'),
            ]),
        (petpvc, suvrpvc_wf,
            [('out_file', 'suvrcalc.in_file')]),
        (suvrpvc_wf, datasink, [
            ('pickatlas.mask_file', 'suvrpvc.@cerebellarmask'),
            ('suvrcalc.out_file', 'suvrpvc.@suvr'),
            ('segstats.summary_file', 'suvrpvc.@segstats'),
            ]),
        ])
    '''
    return main_wf

def create_html():
    pass
