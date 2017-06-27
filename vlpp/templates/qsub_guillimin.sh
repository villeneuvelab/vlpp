#!/bin/bash
#PBS -l nodes=1:ppn=12
#PBS -l walltime={{walltime}}
#PBS -A {{RAPid}}
#PBS -o {{logDir}}
#PBS -e {{logDir}}
#PBS -N vlpp_batch_{{num}}

module use /sf1/project/yai-974-aa/local/modulefiles
module load VilleneuveLab
source activate vlpp

cd ${PBS_O_WORKDIR}

{% for arg in args %}{% if arg %}
{{bin}} {{arg}} &
sleep 10

{% endif %}{% endfor %}
wait
