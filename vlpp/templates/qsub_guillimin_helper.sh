#!/bin/bash
#PBS -l nodes=1:ppn=2
#PBS -l walltime=1:00:00
#PBS -A <RAPid>
#PBS -o <logDir>
#PBS -e <logDir>
#PBS -N <qsub_name>

module use /sf1/project/yai-974-aa/local/modulefiles
module load VilleneuveLab
source activate vlpp

cd ${PBS_O_WORKDIR}

vlpp -p <path_to_pet_data> -f <path_to_freesurfer> -c <path_to_config.json>

