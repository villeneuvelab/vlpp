#!/bin/bash

antsaffine.sh 3 ${anat} ${pet} pet2anat_

#fslmaths {anat} -mul {brainMask} anat_masked.nii.gz
#ANTS 3 -m MI[anat_masked.nii.gz,${pet},1,32] -o pet2anat_ \
    #-i 0 --use-Histogram-Matching \
    #--number-of-affine-iterations 10000x10000x10000x10000x10000 \
    #--rigid-affine false

ln -s *Affine.txt ${participant}${suffix.pet2anat}

