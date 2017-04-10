# -*- coding: utf-8 -*-


from jinja2 import Environment, FileSystemLoader
from ..lib.utils import APP_DIR
import os
from os.path import abspath as opa

from nipype.interfaces.base import BaseInterface, \
    BaseInterfaceInputSpec, File, TraitedSpec, isdefined, traits
from nipype.utils.filemanip import split_filename


class DashboardInputSpec(BaseInterfaceInputSpec):
    in_files = traits.List(File(exists=True))
    tags = traits.List()
    subject_id = traits.Str(desc='Subject ID')
    base_dir = File()

class DashboardOutputSpec(TraitedSpec):
    html_file = File(exists=True, desc='Dashboard HTML file')

class Dashboard(BaseInterface):
    input_spec = DashboardInputSpec
    output_spec = DashboardOutputSpec

    def _run_interface(self, runtime):
        subject_id = self.inputs.subject_id

        templateDir = os.path.join(APP_DIR, 'templates')
        jinja2Env = Environment(
                loader=FileSystemLoader(templateDir),
                trim_blocks=True,
                )
        tpl = jinja2Env.get_template('index.html')

        # Set mosaic path
        mosaics_info = []
        for f, tag in zip(self.inputs.in_files, self.inputs.tags):
            tag["mosaic_file"] = '../{}'.format(
                    os.path.relpath(f, self.inputs.base_dir))
            mosaics_info.append(tag)

        tags = {
                "mosaics": mosaics_info,
                "subject_id": subject_id,
                }
        htmlCode = tpl.render(**tags)

        self._html_file = opa('dashboard_{}.html'.format(subject_id))
        with open(self._html_file, 'w') as f:
            f.write(htmlCode)

        return runtime

    def _list_outputs(self):
        outputs = self._outputs().get()
        outputs['html_file'] = self._html_file
        return outputs

