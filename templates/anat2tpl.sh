#!/bin/bash

fslmaths ${anat} -mul ${brainmask} anat_masked.nii.gz

#antsRegistrationSyN.sh -d 3 -f $tpl -m anat_masked.nii.gz -o anat2tpl_ -n 12 -t b

antsRegistration --dimensionality 3 --float 0 \
    --output [anat2tpl_,anatInTpl_Warped.nii.gz] --interpolation Linear \
    --winsorize-image-intensities [0.005,0.995] --use-histogram-matching 0 \
    --initial-moving-transform [${tpl},anat_masked.nii.gz,1] \
    --transform Rigid[0.1] \
    --metric MI[${tpl},anat_masked.nii.gz,1,32,Regular,0.25] \
    --convergence [1000x500x250x100,1e-6,10] --shrink-factors 8x4x2x1 \
    --smoothing-sigmas 3x2x1x0vox --transform Affine[0.1] \
    --metric MI[${tpl},anat_masked.nii.gz,1,32,Regular,0.25] \
    --convergence [1000x500x250x100,1e-6,10] --shrink-factors 8x4x2x1 \
    --smoothing-sigmas 3x2x1x0vox --transform BSplineSyN[0.1,26,0,3] \
    --metric CC[${tpl},anat_masked.nii.gz,1,4] \
    --convergence [100x70x50x20,1e-6,10] \
    --shrink-factors 8x4x2x1 --smoothing-sigmas 3x2x1x0vox


ln -s anat2tpl_0GenericAffine.mat ${participant}${publishNames["anat2tpl_aff"]}
ln -s anat2tpl_1Warp.nii.gz ${participant}${publishNames["anat2tpl"]}
ln -s anat2tpl_1InverseWarp.nii.gz ${participant}${publishNames["tpl2anat"]}
