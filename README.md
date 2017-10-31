# Villeneuve Laboratory PET Pipeline (VLPP)

VLPP is an open-source software for analyzing PET images combined with freesurfer output from MRI.

VLPP is builded with the [Nextflow framework][nextflow] which enables scalable and reproducible scientific workflows.

## Usage

`vlpp --pet <> --freesurfer <> --participant <> [-params-file <>]`

###### Mandatories arguments:

- `--pet`: PET file (mnc, nii or nii.gz)
- `--freesurfer`: Freesurfer directory of the participant
- `--participant`: Participant code

###### Optional arguments:

- `--help`: Print vlpp usage
- `-params-file`: Load script parameters from a JSON/YAML file
- `-resume`: Execute the script using the cached results, useful to continue executions that was stopped by an error
- `-h` or `-help`: Print the nextflow usage

## Parameters

Default Parameters:

```
{
    "realign": {
        "ignore": false
    },
    "smooth": {
        "ignore": false,
        "fwhm": 6,
        "maskCSF": false
    },
    "fsReferences": {
        "cerebellumCortex": [8, 47],
        "cerebellumCortexErode": [8, 47],
        "wholeCerebellum": [7, 8, 46, 47],
        "whitematter": [2, 41]
    }
}

```

#### `realign`

Realign frames of your participant
  - `ignore`: set it to `true` if you want to skip this step. Will be automatically ignore if PET data has only one frame.

#### `smooth`

Smooth the data after normalization to T1w space
  - `ignore`: set it to `true` if you want to skip this step.
  - `fwhm`: gaussian kernel in mm.
  - `maskCSF`: keep only grey and white matter during the smoothing step.

#### `fsReferences`

Define regions of reference based on freesurfer indices of aparc+aseg atlas.

## Using the pipeline on `guillimin`

Please follow this [link][guillimin-doc].

## Install

Clone this repository and add the `vlpp` and `scripts` direcetories to your `PATH`

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
