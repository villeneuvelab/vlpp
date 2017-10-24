# Villeneuve Laboratory PET Pipeline (VLPP)

<description>

VLPP is builded with the [Nextflow framework][nextflow] which enables scalable and reproducible scientific workflows written in the most common scripting languages.

## Usage

`vlpp --pet <> --freesurfer <> --participant <> [-params-file <>]`

###### Mandatories arguments:

- `--pet`: PET file, it could be .mnc, .nii or .nii.gz
- `--freesurfer`: Freesurfer directory of the participant
- `--participant`: Participant code name

###### Optional arguments:

- `--help`: Print vlpp usage
- `-params-file`: Load script parameters from a JSON/YAML file
- `-resume`: Execute the script using the cached results, useful to continue executions that was stopped by an error
- `-h` or `-help`: Print the nextflow usage

###### List of possible parameters for `-params-file`

Some steps are already automatics but some need parameters

- `dataset`: Specific parameters for some dataset are already build in the pipeline. If this parameter is not set, default parameters will be chosen.
  - `PAD`: for [PreventAD][pad] data
  - `DIAN`: for [DIAN][dian] data
- `realign`: realign frames of your participant
  - set to `ignore` if you want to skip it. Will be automatically ignore if PET data have only one frame.
- `smooth`: smooth the data after normalization to T1w space
  - set to `ignore` if you want to skip it
  - `x` mm (default: 6)
- `mask-smooth`: keep only grey and white matter during the smoothing process

Example of JSON params file:

```
{
    "study": "PAD",
    "realign": "ignore",
    "maskSmooth": true
}
```

## Using the pipeline on `guillimin`

Please follow this [link][guillimin-doc].

## Install

Clone this repository and add the `vlpp` and `scripts` to your `PATH`

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
