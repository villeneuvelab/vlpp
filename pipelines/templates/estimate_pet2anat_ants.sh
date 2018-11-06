#!/bin/bash


if [[ "${transitional}" == "false" ]]

then
    antsaffine.sh 3 ${anat} ${pet} pet2anat_
    ln -s *Affine.txt ${participant}${suffix.pet2anat}

else
    transitionalPet="${transitional}/tmp/*tmp-estimate.nii.gz"
    #transitionalAff="${transitional}/transform/*${suffix.pet2anat}"

    antsaffine.sh 3 \${transitionalPet} ${pet} pet2transitional_
    ln -s *Affine.txt ${participant}${suffix.pet2anat}
    #antsaffine.sh 3 \${transitionalPet} ${pet} pet2transitional_
    #ANTSAverage3DAffine.sh ${participant}${suffix.pet2anat} pet2transitional_Affine.txt \${transitionalAff}

fi

