# -*- coding: utf-8 -*-


import os
import pandas as pd
import time
from itertools import zip_longest
from jinja2 import Environment, FileSystemLoader
from jsonmerge import merge
from subprocess import call
import sys

from .utils import APP_DIR, PIPELINENAME


class Qsub(object):

    def __init__(self, args):
        self.wd = os.getcwd()
        self.codeDir = os.path.join(self.wd, "code")
        self.logDir = os.path.join(self.wd, "log")
        if not os.path.exists(self.codeDir): os.makedirs(self.codeDir)
        if not os.path.exists(self.logDir): os.makedirs(self.logDir)

        self.tags = {
                "RAPid": args.rapid,
                "logDir": self.logDir,
                }

        self.qa = args.qa

        if self.qa:
            self.chunkNum = 8
            self.in_dir = os.path.join(self.wd, 'output')
            self.tags["walltime"] = "1:00:00"
        else:
            self._validation(vars(args))
            self.chunkNum = 8
            self.pet_dir = os.path.abspath(args.pet_dir)
            self.fs_dir = os.path.abspath(args.fs_dir)
            self.tsv = args.tsv
            self.tags["walltime"] = "1:00:00"



    def _validation(self, args):
        for arg in ("pet_dir", "fs_dir", "tsv"):
            if not args[arg]:
                msg = "The following argument is required: --{}"
                sys.exit(msg.format(arg))


    def run(self):
        if self.qa:
            self.tags["bin"] = "vlpp-qa"
            self._run_qa()
        else:
            self.tags["bin"] = "vlpp"
            self._run_vlpp()


    def _run_qa(self):
        for num, chunk in enumerate(
                zip_longest(*[iter(self.participants)]*self.chunkNum)):
            numStr = "qa_{:03d}".format(num)
            qsubName = "{}_{}.sh".format(PIPELINENAME.lower(), numStr)
            qsubScript = os.path.join(self.codeDir, qsubName)

            tags = merge(self.tags, {"num":numStr, "args":chunk})
            self.tpl.stream(**tags).dump(qsubScript)

            call("qsub {}".format(qsubScript), shell=True)
            time.sleep(0.25)


    def _run_vlpp(self):

        base = pd.read_csv(self.tsv, delimiter='\t', dtype=object)

        args = []
        for sub in base["participant_id"]:
            sub_pet = base.loc[base['participant_id'] == sub, 'pet_dir'].iloc[0]
            sub_fs = base.loc[base['participant_id'] == sub, 'fs_dir'].iloc[0]
            args.append("-p {} -i {} -f {}".format(
                    os.path.join(self.pet_dir, sub_pet),
                    sub,
                    os.path.join(self.fs_dir, sub_fs),
                    ))

        for num, chunk in enumerate(zip_longest(*[iter(args)]*self.chunkNum)):
            numStr = "{:03d}".format(num)
            qsubName = "{}_batch_{}.sh".format(PIPELINENAME.lower(), numStr)
            qsubScript = os.path.join(self.codeDir, qsubName)

            tags = merge(self.tags, {"num":numStr, "args":chunk})
            self.tpl.stream(**tags).dump(qsubScript)

            call("qsub {}".format(qsubScript), shell=True)
            time.sleep(0.25)


    @property
    def tpl(self):
        env = Environment(
                loader=FileSystemLoader(os.path.join(APP_DIR, 'templates')),
                trim_blocks=True,
                )
        return env.get_template("qsub_guillimin.sh")


    @property
    def participants(self):
        """
        """
        participants = []
        for fname in os.listdir(self.in_dir):
            path = os.path.join(self.in_dir, fname)
            if (
                    ((fname != 'QA') or (fname != 'working_dir'))
                    and (os.path.isdir(path))):
                participants.append("-i {}".format(fname))
            else:
                pass
        return participants
