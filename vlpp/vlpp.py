# -*- coding: utf-8 -*-


import os
import sys

from nipype import config
from nipype import logging

import nipype.interfaces.io as nio
import nipype.interfaces.utility as niu
import nipype.pipeline.engine as pe

from .lib import utils


def main_workflow(config_dict):

    # Usefull variables
    output_dir = config_dict['arguments']['output_dir']
    working_dir = config_dict['arguments']['working_dir']
    user_debug = config_dict['arguments']['debug']
    pet_dir = config_dict['arguments']['pet_dir']
    fs_dir = config_dict['arguments']['fs_dir']
    subject_id = config_dict['arguments']['subject_id']


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
    wf = pe.Workflow(name=utils.__PIPELINENAME__)
    wf.base_dir = working_dir


    # Infosource
    infields = ['subject_id']
    infosource = pe.Node(niu.IdentityInterface(fields=infields), 'infosource')
    infosource.inputs.subject_id = subject_id


    # PET Files
    templates = {
        "frametimes": "",
        "petframes": "",
        }
    templates.update(config_dict['selectfiles'])
    petfiles = pe.Node(nio.SelectFiles(templates), 'petfiles')
    petfiles.inputs.base_directory = pet_dir
    petfiles.inputs.sort_filelist = True
    #petfiles.inputs.raise_on_empty = False


    # Freesurfer source
    fssource = pe.Node(nio.FreeSurferSource(), 'fssource')
    fssource.inputs.subjects_dir = os.path.dirname(fs_dir)
    fssource.inputs.subject_id = os.path.basename(fs_dir)


    # Datasink
    datasink = pe.Node(nio.DataSink(), 'datasink')
    datasink.inputs.base_directory = output_dir
    substitutions = [
            ('_subject_id_', ''),
            ('_fwhm_6', ''),
            ]
    datasink.inputs.substitutions = substitutions


    # General connections
    wf.connect([
        (infosource, petfiles, [[_] *2 for _ in infields]),
        #(infosource, datasink, [('subject_id', 'container')]),
        ])
    wf.add_nodes([datasink, fssource])


    # Worflows

    ## Preparation
    from .workflows.preparation import Preparation
    _tag = 'preparation'
    preparation = Preparation(config_dict[_tag], _tag).wf
    if preparation is not None:
        wf.connect([
            #(petfiles, preparation, [('frametimes', 'inputnode.frametimes')]),
            (petfiles, preparation, [('petframes', 'inputnode.pet')]),
            (fssource, preparation, [('T1', 'inputnode.anat')]),
            (fssource, preparation, [('aparc_aseg', 'inputnode.atlas')]),
            (preparation, datasink, [
                ('outputnode.pet', 'Preparation.@pet'),
                ('outputnode.anat', 'Preparation.@anat'),
                ('outputnode.atlas', 'Preparation.@atlas'),
                ]),
            ])


    ## Smoothing
    from .workflows.smoothing import Smoothing
    _tag = 'smoothing'
    smoothing = Smoothing(config_dict[_tag], _tag).wf
    if smoothing is not None:
        wf.connect([
            (preparation, smoothing, [('outputnode.pet', 'inputnode.pet')]),
            (smoothing, datasink, [('outputnode.pet', 'Smoothing.@pet')]),
            ])


    ## Realign
    #from .workflows.realign import Realign
    #_tag = 'realign'
    #realign = Realign(config_dict[_tag], _tag).wf
    realign = None
    if realign is not None:
        pass


    ## PET and Anat registration
    from .workflows.anatreg import Anatreg
    _tag = 'anatregistration'
    anatreg = Anatreg(config_dict[_tag], _tag).wf
    if anatreg is not None:
        if realign is None:
            wf.connect([
                (smoothing, anatreg, [('outputnode.pet', 'inputnode.pet')]),
                ])
        else:
            """
            wf.connect([
                (realign, anatreg, [
                    ('calcmean50to70.out_file', 'coregister.source'),
                    ('tile_data.realigned_files', 'coregister.apply_to_files'),
                    ]),
               (anareg, datasink, [('coregister.coregistered_files', 'T1registration.@files')]),
               ])
            """
            pass

        wf.connect([
            (preparation, anatreg, [('outputnode.anat', 'inputnode.anat')]),
            (anatreg, datasink, [('outputnode.pet', 'AnatRegistration.@pet')]),
            ])


    ## Anat and Template registration
    #from .workflows.tplreg import Tplreg
    #_tag = 'templateregistration'
    #tplreg = Tplreg(config_dict[_tag], _tag).wf
    tplreg = None
    if tplreg is not None:
        pass


    ## Segmentation
    from .workflows.segmentation import Segmentation
    _tag = 'segmentation'
    segmentation = Segmentation(config_dict[_tag], _tag).wf
    if segmentation is not None:
        wf.connect([
            (preparation, segmentation,
                [('outputnode.anat', 'inputnode.anat')]),
            (anatreg, segmentation,
                [('outputnode.anatnii', 'inputnode.anatnii')]),
            (segmentation, datasink,
                [('outputnode.seg', 'Segmentation')]),
            ])


    '''
    # SUVR
    from .workflows.suvr import Suvr
    suvr = Suvr(config_dict['suvr'], 'Suvr')
    suvr.implement(wf)

    # Segstats
    from .workflows.segstats import Segstats
    segstats = Segstats(config_dict['segstats'], 'Segstats')
    segstats.implement(wf)

    # QA
    from .workflows.qa import Qa
    qa = Qa(config_dict['qa'], 'Qa')
    qa.implement(wf)

    #PVC
    from interfaces.petpvc import PETPVC
    petpvc = pe.Node(
            PETPVC(**config_dict["pvc"]["params"]),
            'petpvc')
    wf.connect([
        (t1registration, petpvc, [('coregister.coregistered_source', 'in_file')]),
        (segmentation, petpvc, [('merge.merged_file', 'mask_file')]),
        ])

    #SUVR-PVC
    suvrpvc_wf = suvr_wf.clone(name='SUVR_PVC')

    wf.connect([
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
    return wf

def create_html():
    pass
