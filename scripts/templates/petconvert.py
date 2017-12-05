#!/usr/bin/env python
# -*- coding: utf-8 -*-


from vlpp.utils import splitext_
from subprocess import call


def main():
    img = "${img}"
    _, ext = splitext_(img)
    output = "${participant}${suffix.pet}"

    if ext == ".mnc":
        call("mnc2nii -nii -short {0} petconvert.nii".format(img), shell=True)
        call("fslmaths petconvert.nii -nan {0}".format(output), shell=True)
    elif ext in [".nii", ".nii.gz"]:
        call("fslmaths {0} -nan {1}".format(img, output), shell=True)


if __name__ == '__main__':
    main()
