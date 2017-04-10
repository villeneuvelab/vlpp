# VLPP: Villeneuve Laboratory PET Pipeline

## Using it at the lab

### Setting up you environment

If you have access to guillimin cluster, the pipeline is already installed.
You have to setup your environment correctly:

```
ssh -Y <username>@guillimin.hpc.mcgill.ca
module use /sf1/project/yai-974-aa/local/modulefiles
module load VilleneuveLab
source activate vlpp
```

## Using the pipeline

### Prepare your data

Create a directory to launch all the commands

```
mkdir vlpp_processing
cd vlpp_processing
```

#### `vlpp-prepare`

The tool `vlpp-prepare` is here to help setting things up for several subjects.

Here is how to use it: `vlpp-prepare -f <SUBJECTS_DIR> -p <PET_DIR> -c <CSV_FILE>`

- `SUBJECTS_DIR`: this is your freesurfer SUBJECTS_DIR
- `PET_DIR`: same concept 
- `CSV_FILE`: with tree columns: `subject_id`, `fs_dir`, `pet_dir`

Example with data structures like this:

```
/path
  |--freesurfer
    |--subjects
      |--subject_00_type1
      |--subject_01_type1
/other_path
  |--data
    |--pet
      |--subject_00_20170308
      |--subject_01_20170315
```

You could launch vlpp-prepare like this:

`vlpp-prepare -f /path/freesurfer/subjects -p /other_path/data/pet -c <CSV_FILE>`

with a csv file like this:

| subject_id | fs_dir | pet_dir |
| --- | --- | --- |
| subject_00 | subject_00_type1 | subject_00_20170308 |
| subject_01 | subject_01_type1 | subject_01_20170315 |




## Install

```
git clone --recursive https://github.com/villeneuvelab/vlpp.git
```

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
