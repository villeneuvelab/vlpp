#!/bin/bash
#PBS -l procs=12
#PBS -l walltime=1:00:00
#PBS -A yai-974-aa

module use /sf1/project/yai-974-aa/local/modulefiles
module load VilleneuveLab
module load vlpp/dev
source activate vlpp-env

vlpp -c /gs/scratch/cbedetti/PAD115095_NAV_qsub_hand.json

{
    "arguments": {
        "pet_dir": "{{pet_dir}}",
        "fs_dir": "{{fs_dir}}",
        "subject_id": "{{subject_id}}",
        "output_dir": ".",
        "working_dir": "../scratch"
    },
    "selectfiles": {
        "petframes": "*_4D_*1.mnc"
    },
    "realign": {
        "ignore": true
    }
}

