# -*- coding: utf-8 -*-


import os
import sys

from nipype import config
from nipype import logging

import nipype.interfaces.io as nio
import nipype.interfaces.utility as niu
import nipype.pipeline.engine as pe

from .lib import utils


def compute_substitution(config):
    rsl = []

    rsl.append(('_subject_id_', ''))

    for s in config["smoothing"]["fwhm"]:
        val = "fwhm_{}".format(s)
        rsl.append(("_{}".format(val), val))

    for name, l in config["suvr"]["pickatlas"]["labels"].items():
        in_str = "_labels_{}".format(".".join(map(str, l)))
        rsl.append((in_str, name))

    return rsl


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
    substitutions = compute_substitution(config_dict)
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
    '''
    from .workflows.realign import Realign
    _tag = 'realign'
    realign = Realign(config_dict[_tag], _tag).wf
    if realign is not None:
        pass
    '''
    realign = None


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
            (anatreg, datasink, [('outputnode.pet', 'Anatregistration.@pet')]),
            ])


    ## Anat and Template registration
    '''
    from .workflows.tplreg import Tplreg
    _tag = 'templateregistration'
    tplreg = Tplreg(config_dict[_tag], _tag).wf
    if tplreg is not None:
        pass
    '''


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


    # SUVR
    from .workflows.suvr import Suvr
    _tag = 'suvr'
    suvr = Suvr(config_dict[_tag], _tag).wf
    if suvr is not None:
        wf.connect([
            (preparation, suvr, [('outputnode.atlas', 'inputnode.atlas')]),
            (anatreg, suvr, [('outputnode.pet', 'inputnode.pet')]),
            (suvr, datasink, [
                ('outputnode.mask', 'Suvr.@mask'),
                ('outputnode.suvr', 'Suvr.@suvr'),
                ]),
            ])


    # Statsrois
    from .workflows.statsrois import Statsrois
    _tag = 'statsrois'
    statsrois = Statsrois(config_dict[_tag], _tag).wf
    if statsrois is not None:
        wf.connect([
            (preparation, statsrois, [('outputnode.atlas', 'inputnode.atlas')]),
            (suvr, statsrois, [('outputnode.suvr', 'inputnode.suvr')]),
            (statsrois, datasink, [('outputnode.stats', 'Statsrois.@stats')]),
            ])


    '''
    # QA
    from .workflows.qa import Qa
    qa = Qa(config_dict['qa'], 'Qa')
    qa.implement(wf)
    '''

    # Partial Volume Correction
    from .workflows.pvc import Pvc
    _tag = 'pvc'
    pvc = Pvc(config_dict[_tag], _tag).wf
    pvc = None
    if pvc is not None:
        wf.connect([
            (anatreg, pvc, [('outputnode.pet', 'inputnode.pet')]),
            (segmentation, pvc, [('outputnode.seg', 'inputnode.seg')]),
            (pvc, datasink, [('outputnode.petpvc', 'Petpvc.@petpvc')]),
            ])


    # PVC SUVr
    pvcsuvr = suvr.clone(name='Pvcsuvr')
    if pvc is not None:
        wf.connect([
            (preparation, pvcsuvr, [('outputnode.atlas', 'inputnode.atlas')]),
            (pvc, pvcsuvr, [('outputnode.petpvc', 'inputnode.pet')]),
            (pvcsuvr, datasink, [
                ('outputnode.mask', 'PvcPetsuvr.@mask'),
                ('outputnode.suvr', 'PvcPetsuvr.@suvr'),
                ]),
            ])


    # PVC SUVr Statsrois
    pvcstatsroi = statsrois.clone(name='PvcsuvrStatsrois')
    if pvc is not None:
        wf.connect([
            (preparation, pvcstatsrois, [('outputnode.atlas', 'inputnode.atlas')]),
            (pvcsuvr, pvcstatsrois, [('outputnode.suvr', 'inputnode.suvr')]),
            (statsrois, datasink, [('outputnode.stats', 'PvcStatsrois.@stats')]),
            ])


    return wf
