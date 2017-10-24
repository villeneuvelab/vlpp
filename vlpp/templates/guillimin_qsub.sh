#!/bin/bash
#PBS -l nodes=1:ppn=12
#PBS -l walltime={{walltime}}
#PBS -A {{RAPid}}
#PBS -o {{logDir}}
#PBS -e {{logDir}}
#PBS -N vlpp_{{participant}}

module purge
module use /sf1/project/yai-974-aa/local/modulefiles
module load VilleneuveLab

cd ${PBS_O_WORKDIR}
mkdir -p {{participant}}
cd {{participant}}

vlpp --pet {{pet}} --freesurfer {{freesurfer}} --participant {{participant}} -params-file ../code/config.json -resume

cd ${PBS_O_WORKDIR}
