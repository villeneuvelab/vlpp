# VLPP: Villeneuve Laboratory PET Pipeline

## Launch

### Setting up you environment

The pipeline is available on guillimin cluster.
You have to setup your environment correctly: 

```
export SOFT_DIR=/sf1/project/yai-974-aa/local
module use ${SOFT_DIR}/modulefiles
module load VilleneuveLab
source activate vlpp
```

###

```
mkdir vlpp_processing
cd vlpp_processing/
vlpp-prepare -p <PET_DIR> -f <SUBJECTS_DIR> -c <CSV_FILE>
```


## Install

### Software dependencies

- [matlab](https://www.mathworks.com/)
- [spm](http://www.fil.ion.ucl.ac.uk/spm/)
- [fsl](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/)
- [freesurfer](https://surfer.nmr.mgh.harvard.edu/)
- https://github.com/SIMEXP/brainsprite.js.git
- https://github.com/keen/dashboards.git

### Python dependencies

The file `environment.yml` contains the python dependencies. Installing through [conda](https://conda.io/docs/) is highly recommended.

#### Create the environment `vlpp`

```
conda config --add channels conda-forge
conda env create -f environment.yml
```

#### Update the environment

`conda env update -f environment.yml`

## Output

### scratch directory

## Informations

Developer and maintainer: *Christophe Bedetti*

*Warning: Project under active development, process data at your own risk !!*
