#!/bin/bash
#PBS -l procs=12
#PBS -l walltime={{walltime}}
#PBS -l pmem=2700mb
#PBS -j oe
#PBS -A {{RAPid}}
#PBS -N {{jobname}}
#PBS -o {{logDir}}
#PBS -e {{logDir}}

module use /sf1/project/yai-974-aa/local/modulefiles
module load VilleneuveLab
source activate vlpp

cd ${PBS_O_WORKDIR}

{% if qa %}
vlpp-qa
{% else %}
vlpp -c {{json}}
{% endif %}

