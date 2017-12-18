# Villeneuve Laboratory PET Pipeline (VLPP)

VLPP is an open-source software for analyzing PET images combined with freesurfer.

VLPP is builded with the [Nextflow framework][nextflow] which enables scalable and reproducible scientific workflows.

## Usage

`vlpp --pet <> --freesurfer <> --participant <> [-c <>]`

###### Mandatories arguments:

- `--pet`: PET file (`mnc`, `nii` or `nii.gz`)
- `--freesurfer`: Freesurfer directory of the participant
- `--participant`: Participant code

###### Optional arguments:

- `--help`: Print vlpp usage
- `-c, -config`: Add the specified file to configuration set
- `-resume`: Execute the script using the cached results, useful to continue executions that was stopped by an error
- `-h` or `-help`: Print the nextflow usage

## Configurations

Default Parameters and explanation: see `config/default.config`

## Using the pipeline on `guillimin`

Please follow this [link][guillimin-doc].

## Install

Clone this repository and add the `vlpp` and `scripts` directories to your `PATH`.

###### Software dependencies

- [matlab](https://www.mathworks.com/)
- [spm](http://www.fil.ion.ucl.ac.uk/spm/)
- [fsl](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/)
- [freesurfer](https://surfer.nmr.mgh.harvard.edu/)
- [ANTs](http://stnava.github.io/ANTs/)
- [minctools](http://www.bic.mni.mcgill.ca/ServicesSoftware/MINC)
- [Nextflow][nextflow]

### Python dependencies

The files `environment.yml` and `requirements.txt` contains the python dependencies

If you use conda [conda](https://conda.io/docs/). Here is how to install the python environment:

```
conda config --add channels conda-forge
conda config --add channels bioconda
conda env create -f environment.yml
```

[dian]: https://www.nia.nih.gov/alzheimers/clinical-trials/dominantly-inherited-alzheimer-network-dian
[guillimin-doc]: https://github.com/villeneuvelab/documentation/wiki/VLPP-on-guillimin
[nextflow]: https://www.nextflow.io/
[pad]: http://www.douglas.qc.ca/page/prevent-alzheimer
