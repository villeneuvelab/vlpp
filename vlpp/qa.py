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


class Qa(object):

    def __init__(self, vlpp_dir):
        self.vlpp_dir = vlpp_dir
        self.wf = set_wf()


    def run(self):
        self.wf.run()


    @property
    def subjects(self):
        """
        """
        subjects = []
        for fname in os.listdir(self.vlpp_dir):
            path = os.path.join(self.vlpp_dir, fname)
            if (fname != 'QA') and (os.path.isdir(path)):
                subjects.append(fname)
            else:
                pass
        return subjects


    def set_wf(self):

        # Usefull variables
        output_dir = os.path.join(self.vlpp_dir, "QA")
        """
        output_dir = config_dict['arguments']['output_dir']
        working_dir = config_dict['arguments']['working_dir']
        #user_debug = config_dict['arguments']['debug']
        pet_dir = config_dict['arguments']['pet_dir']
        fs_dir = config_dict['arguments']['fs_dir']
        subject_id = config_dict['arguments']['subject_id']
        """


        # Directories
        for directory in [output_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)


        # Nipype configuration
        config.update_config({'logging': {'log_directory': output_dir}})
        #config.logging.log_directory = output_dir
        #if user_debug:
        #    config.enable_debug_mode()
        logging.update_logging(config)


        # Main workflow
        wf = pe.Workflow(name="{}-QA".format(utils.PIPELINENAME))
        wf.base_dir = qa_dir


        # Infosource
        infields = ['subject_id']
        infosource = pe.Node(niu.IdentityInterface(fields=infields), 'infosource')
        #infosource.inputs.subject_id = subject_id
        print(self.subjects)
        infosource.iterables = [('subject_id', self.subjects)]


        # SelectFiles
        templates = {
                "anat": "mri/T1_out.nii.gz",
                "atlas": "mri/aparc+aseg_out.nii.gz",
                }
        petfiles = pe.Node(nio.SelectFiles(templates), 'selectfiles')
        petfiles.inputs.base_directory = self.vlpp_dir
        petfiles.inputs.sort_filelist = True
        #petfiles.inputs.raise_on_empty = False


        # Datasink
        datasink = pe.Node(nio.DataSink(), 'datasink')
        datasink.inputs.base_directory = output_dir
        #substitutions = compute_substitution(config_dict)
        #datasink.inputs.substitutions = substitutions


        # General connections
        wf.connect([
            (infosource, selectfiles, [[_] *2 for _ in infields]),
            #(infosource, datasink, [('subject_id', 'container')]),
            ])
        wf.add_nodes([datasink])


        # Worflows

        # QA
        from .workflows.qa import Qa
        qa = Qa(config_dict['qa'], 'Qa')
        qa.implement(wf)


        return wf

"""
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
"""
