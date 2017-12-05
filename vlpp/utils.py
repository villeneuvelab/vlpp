#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
#from subprocess import call
#from jinja2 import Environment, FileSystemLoader


def splitext_(path):
    for ext in ['.nii.gz']:
        if path.endswith(ext):
            return path[:-len(ext)], path[-len(ext):]
    return os.path.splitext(path)

