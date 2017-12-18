#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
from vlpp.utils import add_suffix
from vlpp.registration import applyAnat2Tpl


def main():
    os.mkdir("anat")
    os.mkdir("pet")
    os.mkdir("centiloid")

    anat = "${anat}"
    atlas = "${atlas}"
    pet4070 = "${pet4070}"
    pet5070 = "${pet5070}" #centiloid

    anat2tpl = "${anat2tpl}"

    for img, _dir, tag, interp in zip(
            [anat, atlas, pet4070, pet5070],
            ["anat", "anat", "pet", "centiloid"],
            ["anat", "atlas", "pet", "centiloid"],
            [4, 0, 4, 4],
            ):

        output = img.replace("_space-anat", "")
        output = os.path.join(_dir, add_suffix(output, "space-tpl"))

        applyAnat2Tpl(img, anat2tpl, interp, tag, output)


if __name__ == '__main__':
    main()

