#!/bin/bash
#SBATCH --job-name=vlpp_{{participant}}
#SBATCH --nodes=1
#SBATCH --mem=0
#SBATCH --time={{walltime}}
#SBATCH --account={{RAPid}}
#SBATCH --output={{logDir}}/%x-%j.out


export VL_QUARANTINE_DIR="/project/ctb-villens/quarantine"
module use ${VL_QUARANTINE_DIR}/modulefiles
module load VilleneuveLab

{% if dev %}

module load vlpp/dev
source ${VL_QUARANTINE_DIR}/python_virtualenv/vlpp-dev/bin/activate

{% else %}

module load vlpp/prod
source ${VL_QUARANTINE_DIR}/python_virtualenv/vlpp/bin/activate

{% endif %}


# Checking if SLURM_SUBMIT_DIR exists
# If not, write some basic log in the HOME directory and exit
if [ -d "${SLURM_SUBMIT_DIR}" ]
then
    cd ${SLURM_SUBMIT_DIR}
else
    _logFile=${HOME}/vlpp_{{participant}}.e${SLURM_JOB_ID}
    echo "HOSTNAME="$(hostname) > ${_logFile}
    env | grep SLURM >> ${_logFile}
    date >> ${_logFile}
    echo >> ${_logFile}
    echo "SLURM_SUBMIT_DIR does not exist" >> ${_logFile}
    exit 1
fi


mkdir -p {{participant}}
cd {{participant}}

if [ -f "work.tar.gz" ]
then
    tar zxf work.tar.gz
    rm work.tar.gz
fi

{% if qa %}

vlpp-qa.nf -profile qa
cd ${SLURM_SUBMIT_DIR}
tar zcf qa.tar.gz qa/assets/ qa/data/*js qa/data/*jpg qa/*.html
cd {{participant}}

{% else %}

vlpp.nf --pet {{pet}} --freesurfer {{freesurfer}} --participant {{participant}} -c ../code/config.cfg -resume

{% endif %}

tar zcf work.tar.gz work/
rm -Rf work/

