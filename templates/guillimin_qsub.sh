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


{% if dev %}
module load vlpp/dev
source activate vlpp-dev
{% endif %}


cd ${PBS_O_WORKDIR}
mkdir -p {{participant}}
cd {{participant}}


{% if qa %}
vlpp-qa.nf -resume

{% else %}
vlpp.nf --pet {{pet}} --freesurfer {{freesurfer}} --participant {{participant}} -c ../code/config.cfg -resume

{% endif %}

{% if not dev %}
# Removing work directory if pipeline success
EXITCODE=$?
if [[ $EXITCODE -eq 0 ]]
then
    rm -Rf work/
fi


{% endif %}
cd ${PBS_O_WORKDIR}


{% if qa %}
tar zcvf qa.tar.gz qa/assets/ qa/data/*js qa/data/*jpg qa/*.html
{% endif %}
