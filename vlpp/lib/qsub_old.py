# -*- coding: utf-8 -*-


import glob
from jinja2 import Environment, FileSystemLoader
import os
from subprocess import call
import time

from .utils import APP_DIR


class Qsub(object):

    def __init__(self, args):
        self.wd = os.getcwd()
        self.dry = args.dry
        self.qa = args.qa
        self.codeDir = os.path.join(self.wd, 'code')
        self.tags = {
                "walltime": args.walltime,
                "RAPid": args.rapid,
                "logDir": os.path.join(self.wd, "log"),
                "qa": self.qa,
                }
        logDir = self.tags['logDir']
        if not os.path.exists(logDir):
            os.makedirs(logDir)


    def run(self):
        if self.qa:
            self._run_qa()
        else:
            self._run_vlpp()


    @property
    def tpl(self):
        env = Environment(
                loader=FileSystemLoader(os.path.join(APP_DIR, 'templates')),
                trim_blocks=True,
                )
        return env.get_template("qsub_guillimin.sh")


    def call(self, qsubFile):
        if self.dry:
            pass
        else:
            call("qsub {}".format(qsubFile), shell=True)
            time.sleep(.5)


    def _run_qa(self):
        self.tags["jobname"] = "vlpp_qa"

        qsubFile = os.path.join(self.codeDir, "qsub_qa.sh")
        with open(qsubFile, 'w') as f:
            f.write(self.tpl.render(**self.tags))

        self.call(qsubFile)


    def _run_vlpp(self):

        for json in glob.glob(os.path.join(self.codeDir, '*.json')):
            if "config.json" in json:
                pass
            else:
                jsonFile = os.path.abspath(json)
                sub = os.path.splitext(os.path.basename(json))[0]

                self.tags["jobname"] = "{}_vlpp".format(sub)
                self.tags["json"] = jsonFile

                qsubFile = os.path.join(self.codeDir, "qsub_{}.sh".format(sub))
                with open(qsubFile, 'w') as f:
                    f.write(self.tpl.render(**self.tags))

                self.call(qsubFile)

