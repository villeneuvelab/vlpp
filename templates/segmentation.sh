#!/bin/bash


cp ${anat} anat.nii.gz
gzip -d anat.nii.gz
cp ${baseDir}/templates/segmentation.m .
matlab -nodisplay < segmentation.m
gzip c?anat.nii

mkdir mask
ln -s ../c1anat.nii.gz mask/${participant}_roi-c1${suffix.mask}
ln -s ../c2anat.nii.gz mask/${participant}_roi-c2${suffix.mask}
ln -s ../c3anat.nii.gz mask/${participant}_roi-c3${suffix.mask}
ln -s ../c4anat.nii.gz mask/${participant}_roi-c4${suffix.mask}
ln -s ../c5anat.nii.gz mask/${participant}_roi-c5${suffix.mask}

mkdir transform
ln -s ../y_anat.nii transform/${participant}${suffix.anat2tpl}
ln -s ../iy_anat.nii transform/${participant}${suffix.tpl2anat}

rm anat.nii
ln -s ${anat} anat.nii.gz
