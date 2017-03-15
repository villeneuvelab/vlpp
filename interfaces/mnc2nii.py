# -*- coding: utf-8 -*-


#import os
#from os.path import abspath as opa

#from nipype.interfaces.base import BaseInterface, \
    #BaseInterfaceInputSpec, File, TraitedSpec, isdefined, traits
#from nipype.utils.filemanip import split_filename

from nipype.interfaces.base import (
        TraitedSpec, CommandLineInputSpec, CommandLine, File, isdefined
        )


class InputSpec(CommandLineInputSpec):
    in_file = File(
            desc="File", position=0, exists=True, mandatory=True, argstr="%s")
    #out_file = File(genfile=True, position=1, argstr="%s", desc="image to write", mandatory=False)
    out_file = File(argstr="%s", name_source=['in_file'], hash_files=False, keep_extension=False, name_template='%s.nii', position=1)

class OutputSpec(TraitedSpec):
    out_file = File(desc="Zip file", exists=True)

class Mnc2Nii(CommandLine):
    input_spec = InputSpec
    output_spec = OutputSpec
    _cmd = 'mnc2nii -nii -short'

    '''
    def _gen_filename(self, name):
        head, _, _ = self.inputs.in_file.rpartition('.mnc')
        return head + '.nii'

    def _list_outputs(self):
        outputs = self.output_spec().get()
        if isdefined(self.inputs.out_file):
            outputs["out_file"] = self.inputs.out_file
        else:
            outputs["out_file"] = self._gen_filename()
    '''


