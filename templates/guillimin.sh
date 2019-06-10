#!/bin/bash
#PBS -l nodes=1:ppn=32:hw
#PBS -l walltime={{walltime}}
#PBS -A {{RAPid}}
#PBS -o {{logDir}}
#PBS -e {{logDir}}
#PBS -N vlpp_{{participant}}


source /software/soft.computecanada.ca.sh
export VL_QUARANTINE_DIR="/sf1/project/yai-974-aa/quarantine"
module use ${VL_QUARANTINE_DIR}/modulefiles
module load VilleneuveLab

{% if dev %}

module load vlpp/dev
source ${VL_QUARANTINE_DIR}/python_virtualenv/vlpp-dev/bin/activate

{% else %}

module load vlpp/prod
source ${VL_QUARANTINE_DIR}/python_virtualenv/vlpp/bin/activate

{% endif %}


# Checking if PBS_O_WORKDIR exists
# If not, write some basic log in the HOME directory and exit
if [ -d "${PBS_O_WORKDIR}" ]
then
    cd ${PBS_O_WORKDIR}
else
    _id=$(echo ${PBS_JOBID} | cut -d"." -f1)
    _logFile=${HOME}/vlpp_{{participant}}.e${_id}
    echo "HOSTNAME="${HOSTNAME} > ${_logFile}
    env | grep PBS >> ${_logFile}
    date >> ${_logFile}
    echo >> ${_logFile}
    echo "PBS_O_WORKDIR does not exist" >> ${_logFile}
    exit 1
fi


mkdir -p {{participant}}
cd {{participant}}

{% if qa %}

vlpp-qa.nf -profile qa
cd ${PBS_O_WORKDIR}
tar zcvf qa.tar.gz qa/assets/ qa/data/*js qa/data/*jpg qa/*.html

{% else %}

vlpp.nf --pet {{pet}} --freesurfer {{freesurfer}} --participant {{participant}} -c ../code/config.cfg -resume

{% endif %}
{% if removingWorkingDir %}

# Removing work directory if pipeline success
EXITCODE=$?
if [[ $EXITCODE -eq 0 ]]
then
    rm -Rf work/
fi
{% endif %}
