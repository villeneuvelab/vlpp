# -*- coding: utf-8 -*-


import os
import sys

from nipype import config
from nipype import logging

import nipype.interfaces.io as nio
import nipype.interfaces.utility as niu
import nipype.pipeline.engine as pe

from .lib import utils


class Qa(object):

    def __init__(self, in_dir, config):
        self.in_dir = in_dir
        self.config = config
        self.wf = self.set_wf()


    def run(self):
        self.wf.write_graph(graph2use='colored')
        self.wf.run()


    @property
    def subjects(self):
        """
        """
        subjects = []
        for fname in os.listdir(self.in_dir):
            path = os.path.join(self.in_dir, fname)
            if (fname != 'QA') and (os.path.isdir(path)):
                subjects.append(fname)
            else:
                pass
        return subjects


    def set_wf(self):

        # Usefull variables
        qa_dir = os.path.join(self.in_dir, "QA")


        # Directories
        for directory in [qa_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)


        # Nipype configuration
        config.update_config({'logging': {'log_directory': qa_dir}})
        #config.logging.log_directory = output_dir
        #if user_debug:
        #    config.enable_debug_mode()
        logging.update_logging(config)


        # Main workflow
        wf = pe.Workflow(name="{}_QA".format(utils.PIPELINENAME))
        wf.base_dir = qa_dir


        # Infosource
        infields = ['subject_id']
        infosource = pe.Node(niu.IdentityInterface(fields=infields), 'infosource')
        #infosource.inputs.subject_id = subject_id
        #print(self.subjects)
        infosource.iterables = [('subject_id', self.subjects)]
        #infosource.iterables = [('subject_id', ['PAD115095_NAV'])]


        # SelectFiles
        templates = {
                "anat": "{subject_id}/mri/T1_out.nii.gz",
                "atlas": "{subject_id}/mri/aparc+aseg_out.nii.gz",
                "petreg": "{subject_id}/pet/*/r*mean_maths.nii.gz",
                "mask": "{subject_id}/mask/cerebellum*/*nii.gz",
                "suvr": "{subject_id}/suvr/*/cerebellum*/*maths_suvr.nii.gz",
                }
        selectfiles = pe.Node(nio.SelectFiles(templates), 'selectfiles')
        selectfiles.inputs.base_directory = self.in_dir
        selectfiles.inputs.sort_filelist = True
        #selectfiles.inputs.raise_on_empty = False


        # Dashboards Files
        assets_templates = {
            'bcss': 'dashboards/assets/lib/bootstrap/dist/css/bootstrap.min.css',
            'keencss': 'dashboards/assets/css/keen-dashboards.css',
            'jquery': 'dashboards/assets/lib/jquery/dist/jquery.min.js',
            'bjs': 'dashboards/assets/lib/bootstrap/dist/js/bootstrap.min.js',
            'holder': 'dashboards/assets/lib/holderjs/holder.js',
            'keen': 'dashboards/assets/lib/keen-js/dist/keen.min.js',
            'meta': 'dashboards/assets/js/meta.js',
            'bs': 'brainsprite.js/assets/brainsprite.min.js',
            }
        assetsfiles = pe.Node(nio.SelectFiles(assets_templates), 'assetsfiles')
        assetsfiles.inputs.base_directory = os.path.dirname(utils.APP_DIR)


        # Datasink
        datasink = pe.Node(nio.DataSink(), 'datasink')
        datasink.inputs.base_directory = qa_dir
        #substitutions = compute_substitution(config_dict)
        #datasink.inputs.substitutions = substitutions
        datasink.inputs.substitutions = (('_subject_id_', ''))


        # General connections
        assets_connexions = [
            (k, 'assets.@{}'.format(k)) for k in assets_templates.keys()
            ]
        wf.connect([
            (infosource, selectfiles, [[_] *2 for _ in infields]),
            (assetsfiles, datasink, assets_connexions),
            #(infosource, datasink, [('subject_id', 'container')]),
            ])


        # Worflows

        # Images
        from .workflows.mosaics import Mosaics
        mosaics = Mosaics(self.config['mosaics'], 'Mosaics').wf
        connexions = [(k, 'inputnode.{}'.format(k)) for k in templates.keys()]
        wf.connect([(selectfiles, mosaics, connexions)])


        from .interfaces.dashboard import Dashboard
        dashboard = pe.Node(Dashboard(base_dir=qa_dir), 'dashboard')
        wf.connect([
            (infosource, dashboard, [('subject_id', 'subject_id')]),
            (mosaics, dashboard, [
                ('outputnode.files', 'in_files'),
                ('outputnode.tags', 'tags'),
                ]),
            (dashboard, datasink, [('html_file', '@dashboard')]),
            ])

        return wf

