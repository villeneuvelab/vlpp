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

You need to create a new directory in wich you will run all the commands for the processing, for example:

```
mkdir vlpp_processing
cd vlpp_processing
```

In this tutorial, we suppose that your data have this structure:

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
        |--NAV_subject_00_20170308_1435.nii.gz
      |--subject_01_20170315
        |--NAV_subject_01_20170315_1126.nii.gz
```

### Prepare your data

The tool `vlpp-prepare` is here to help setting things up for several subjects. With this kind of structures you would have to create a `participants.tsv` file with at least 3 columns (participant_id, fs_dir, pet_dir). A tsv (tabulation-separated values) file is the same as a csv file but tabulation is used to separated data.

| participant_id | fs_dir | pet_dir |
| --- | --- | --- |
| subject_00 | subject_00_type1 | subject_00_20170308 |
| subject_01 | subject_01_type1 | subject_01_20170315 |

Now, you can run the command:

`vlpp-prepare -f /path/freesurfer/subjects -p /other_path/data/pet -t participants.tsv`

It will create a `code` directory with a json file for each subjects. Here is an example of `code/subject_00.json`:

```
{
    "arguments": {
        "fs_dir": "/path/freesurfer/subjects/subject_00_type1",
        "pet_dir": "/other_path/data/pet/subject_00_20170308",
        "subject_id": "subject_00"
    }
}
```

The last step is to create the configuration file of your study: `touch code/config.json`. The pipeline will automatically looks into this file and update the default configuration to fit your study. If you want to change a configuration at the subjects level, you will need to edit the json file of the subject in the `code` directory.

The pipeline needs to know how to access your pet data. It is done with a generic string in the `pet` key inside the `selectfiles` configuration. Here is the content of `code/config.json` for the tutorial example:

```
{
    "selectfiles": {
        "pet": "NAV_{participant_id}_*.nii.gz"
    }
}
```

As you can see, it is possible to use the `participant_id` inside curly braces to indicate the participant name.

### Submitting the pipeline on guillimin queues

This is done with `vlpp-qsub` and with your Resource Allocation Project identifier (RAPid). `vlpp-qsub -r <RAPid>`

### Quality Assessment

`vlpp-qsub -r <RAPid> --qa`

## Install

```
git clone --recursive https://github.com/villeneuvelab/vlpp.git
```

### Software dependencies

- [matlab](https://www.mathworks.com/)
- [spm](http://www.fil.ion.ucl.ac.uk/spm/)
- [fsl](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/)
- [freesurfer](https://surfer.nmr.mgh.harvard.edu/)

### Python dependencies

The file `environment.yml` contains the python dependencies. Installing through [conda](https://conda.io/docs/) is highly recommended.

#### Create the environment `vlpp`

```
conda config --add channels conda-forge
conda env create -f environment.yml
```

#### Update the environment

`conda env update -f environment.yml`

