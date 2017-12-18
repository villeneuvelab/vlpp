#!/usr/bin/env python
# -*- coding: utf-8 -*-


from vlpp.utils import splitext_, run_shell, warn


def main():
    img = "${img}"
    _, ext = splitext_(img)
    output = "${participant}${suffix.pet}"

    if ext == ".mnc":
        run_shell("mnc2nii -nii -short {0} petconvert.nii".format(img))
        #run_shell("fslmaths petconvert.nii -nan {0}".format(output))
        run_shell("fslmaths petconvert.nii {0}".format(output))

    elif ext in [".nii", ".nii.gz"]:
        #run_shell("fslmaths {0} -nan {1}".format(img, output))
        run_shell("fslmaths {0} {1}".format(img, output))

    else:
        warn([
            "Process: petconvert",
            "  {} extension is not supported".format(ext),
            "  Converting with mri_convert",
            "  This might fail, check your data",
            ])
        run_shell("mri_convert -ot nii -i {0} -o {1}".format(img, output))


if __name__ == '__main__':
    main()
