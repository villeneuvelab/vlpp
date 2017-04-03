# -*- coding: utf-8 -*-


import glob
from jinja2 import Environment, FileSystemLoader
import os

from .utils import APP_DIR


class Qsub(object):

    def __init__(self, args):
        self.walltime = args.walltime
        self._rapid = args.rapid
        self.dry = args.dry

    @property
    def rapid(self):
        return "yai-974-aa" #Sylvia

    def run(self):

        wd = os.getcwd()
        codeDir = os.path.join(wd, 'code')

        for json in glob.glob('code/*.json'):
            jsonFile = os.path.abspath(json)
            sub = os.path.splitext(os.path.basename(json))[0]

            env = Environment(
                    loader=FileSystemLoader(os.path.join(
                        APP_DIR, 'templates')),
                    trim_blocks=True,
                    )
            tpl = env.get_template("qsub_guillimin.sh")

            logDir = os.path.join(wd, "log")
            if not os.path.exists(logDir):
                os.makedirs(logDir)

            tags = {
                    "walltime": self.walltime,
                    "RAPid": self.rapid,
                    "logDir": logDir,
                    "subject": sub,
                    "json": jsonFile,
                    }

            qsubFile = os.path.join(codeDir, "qsub_{}.sh".format(sub))
            with open(qsubFile, 'w') as f:
                f.write(tpl.render(**tags))

            if self.dry:
                pass
            else:
                call("qsub {}".format(qsubFile), shell=True)
                time.sleep(.5)
