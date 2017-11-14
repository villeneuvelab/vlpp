#!/bin/bash
#PBS -l nodes=1:ppn=12
#PBS -l walltime={{walltime}}
#PBS -A {{RAPid}}
#PBS -o {{logDir}}
#PBS -e {{logDir}}
#PBS -N vlpp_qa

module purge
module use /sf1/project/yai-974-aa/local/modulefiles
module load VilleneuveLab

cd ${PBS_O_WORKDIR}
mkdir -p qa
cd qa

vlpp-qa.nf -resume

cd ${PBS_O_WORKDIR}
tar zcvf qa.tar.gz qa/
