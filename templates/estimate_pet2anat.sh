#!/bin/bash

#antsaffine.sh 3 ${anat} ${pet} pet2anat_

ANTS 3 -m MI[${anat},${pet},1,32] -o pet2anat_ \
    -i 0 --use-Histogram-Matching \
    --number-of-affine-iterations 10000x10000x10000x10000x10000 \
    --rigid-affine false

ln -s pet2anat_Affine.txt ${participant}${suffix["pet2anat"]}

