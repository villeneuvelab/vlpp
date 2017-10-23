# VLPP: Villeneuve Laboratory PET Pipeline

## Using the pipeline on `guillimin`

### Setting up you environment

If you have access to guillimin cluster, the pipeline is already installed.
To be able to use it, you have to setup your environment correctly:

```
ssh -Y <username>@guillimin.hpc.mcgill.ca
module use /sf1/project/yai-974-aa/local/modulefiles
module load VilleneuveLab
```

Please, follow the instructions on "How to access neuroimaging softwares" and "How to setup spm for matlab" from [here](https://github.com/villeneuvelab/documentation/wiki/Guillimin-neuroimaging-softwares)

### Launch with one participant localy

As you can see in the help above, the pipeline needs at least two directories (the one with your PET data and the freesurfer directory.

`vlpp -p <path_to_pet_data> -f <path_to_freesurfer>`

If your PET data is in another format than "*.nii.gz", you can change that through a configuration file (`config.json`):

```
{
    "selectfiles": {
        "pet": "*.mnc"
    }
}
```

`vlpp -p <path_to_pet_data> -f <path_to_freesurfer> -c config.json`

### Launch with one participant with `qsub`

You need to create a new directory in wich you will run the qsub command, for example:

```
mkdir pet_processing
cd pet_processing
```

Create a `code` directory to stock your qsub script (`mkdir code`)

Copy the qsub script template `qsub_guillimin_helper.sh` inside the code directory. On guillimin: `cp /sf1/project/yai-974-aa/local/vlpp/git/vlpp/templates/qsub_guillimin_helper.sh code/qsub_<participant_code>.sh`

Edit this script to your need. [Link to the template](https://github.com/villeneuvelab/vlpp/blob/master/vlpp/templates/qsub_guillimin_helper.sh)

### Launch with several participants

You need to create a new directory in wich you will run all the commands for the processing, for example:

```
mkdir pet_processing
cd pet_processing
```

In this example, we suppose that your data have this structure:

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
        |--NAV_subject_00_20170308_1435.mnc
      |--subject_01_20170315
        |--NAV_subject_01_20170315_1126.mnc
```

#### configuration file

This step is optional and is needed if you want to run the pipeline with different options than the default (see here for more informations). Inside your processing directory, create a `code` directory with a new `config.json` file. The pipeline will automatically looks into this file and update the default configuration to fit your study.

```
mkdir code
touch code/config.json
```

The pipeline needs to know how to access your pet data. It is done with a generic string in the `pet` key inside the `selectfiles` configuration. Here is the content of `code/config.json` for the tutorial example:

```
{
    "selectfiles": {
        "pet": "NAV_{participant_id}_*.nii.gz"
    }
}
```

Since there is only one _minc_ file in the example, the value could simply be "*.mnc". The example above was to show, it is possible to use the `participant_id` inside curly braces to indicate the participant name.

#### `vlpp-qsub`

```
$ vlpp-qsub -h
usage: vlpp-qsub [-h] [-p PET_DIR] [-f FS_DIR] [-t TSV] [-r RAPID] [--qa]

optional arguments:
  -h, --help            show this help message and exit
  -p PET_DIR, --pet_dir PET_DIR
                        Base directory for all of your PET data
  -f FS_DIR, --fs_dir FS_DIR
                        Base directory for all of your freesurfer data
  -t TSV, --tsv TSV     A tsv file describing your participants
  -r RAPID, --rapid RAPID
                        Your RAPid number on guillimin
  --qa                  Launch the quality assessment
```

The tool `vlpp-qsub` is here to help submitting the pipeline through `qsub` on guillimin. With this kind of structure (describe above) you would have to create a `participants.tsv` file with at least 3 columns (participant_id, fs_dir, pet_dir). A tsv (tabulation-separated values) file is the same as a csv file but tabulation is used to separated data.

| participant_id | fs_dir | pet_dir |
| --- | --- | --- |
| subject_00 | subject_00_type1 | subject_00_20170308 |
| subject_01 | subject_01_type1 | subject_01_20170315 |

Now, you can run the command:

`vlpp-qsub -f /path/freesurfer/subjects -p /other_path/data/pet -t participants.tsv`

#### Quality Assessment

`vlpp-qsub --qa`

## Install

```
git clone --recursive https://github.com/villeneuvelab/vlpp.git
```

### Software dependencies

- [matlab](https://www.mathworks.com/)
- [spm](http://www.fil.ion.ucl.ac.uk/spm/)
- [fsl](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/)
- [freesurfer](https://surfer.nmr.mgh.harvard.edu/)
- [ANTs](http://stnava.github.io/ANTs/)

### Python dependencies

The file `environment.yml` contains the python dependencies. Installing through [conda](https://conda.io/docs/) is highly recommended.

#### Create the environment `vlpp`

```
conda config --add channels conda-forge
conda config --add channels bioconda
conda env create -f environment.yml
```

#### Update the environment

`conda env update -f environment.yml`

