# -*- coding: utf-8 -*-


from nipype.interfaces.base import (
        TraitedSpec, CommandLineInputSpec, CommandLine, File, traits
        )


class InputSpec(CommandLineInputSpec):
    #type = traits.String()
    in_file = File(
            position=0, desc="minc file", argstr="%s",
            exists=True, mandatory=True,
            )
    out_file = File(
            position=1, desc="nifti output file", argstr="%s", hash_files=False,
            name_source=['in_file'], keep_extension=False, name_template='%s.nii',
            )

class OutputSpec(TraitedSpec):
    out_file = File(desc="nifti output file", exists=True)

class Mnc2Nii(CommandLine):
    input_spec = InputSpec
    output_spec = OutputSpec
    _cmd = 'mnc2nii -nii -short'

