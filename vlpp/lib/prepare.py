# -*- coding: utf-8 -*-


import os
import pandas as pd

from .utils import APP_DIR, write_json


class Prepare(object):

    def __init__(self, args):
        self.pet_dir = os.path.abspath(args.pet_dir)
        self.fs_dir = os.path.abspath(args.fs_dir)
        self.tsv = args.tsv

    def run(self):

        wd = os.getcwd()

        codeDir = os.path.join(wd, "code")
        if not os.path.exists(codeDir):
            os.makedirs(codeDir)

        base = pd.read_csv(self.tsv, delimiter='\t', dtype=object)

        for sub in base["participant_id"]:
            sub_pet = base.loc[base['participant_id'] == sub, 'pet_dir'].iloc[0]
            sub_fs = base.loc[base['participant_id'] == sub, 'fs_dir'].iloc[0]
            jsonCode = {
                    "arguments": {
                        "participant_id": sub,
                        "pet_dir": os.path.join(self.pet_dir, sub_pet),
                        "fs_dir": os.path.join(self.fs_dir, sub_fs),
                        }
                    }

            jsonFile = os.path.join(codeDir, '{}.json'.format(sub))
            if os.path.exists(jsonFile):
                print("{}: json already exists, remove first and relaunch this script".format(sub))
            else:
                write_json(jsonCode, jsonFile)
                print("{}: json created".format(sub))

