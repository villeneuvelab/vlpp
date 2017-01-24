# -*- coding: utf-8 -*-


import json
import os
import sys


__PIPELINENAME__ = 'VLPP'
PROD_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


def load_json(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
    return data


def write_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4, sort_keys=True)


def get_subjects(input_dir):
    subject_list = []
    for fname in os.listdir(input_dir):
        path = os.path.join(input_dir, fname)
        if os.path.isdir(path):
            subject_list.append(fname)
        else:
            continue
    return subject_list


def exit():
    sys.exit()


class WorkflowManager(object):

    def __init__(self, config, name):
        self._config = config
        self._name = name
        self._wf = None

    @property
    def config(self):
        return self._config

    @property
    def name(self):
        return self._name

    @property
    def kind(self):
        return self._config['kind']

    @property
    def wf(self):
        return self._wf

    def generate(self):
        raise NotImplementedError

    def connect(self, main_wf):
        raise NotImplementedError

    def exit(self):
        #TODO implement this function with nipype error or logging ?
        msg = "'{}' is not implemented for the {} workflow"
        print(msg.format(self.kind, self.name))


#TODO: old code to delete
"""
def script_path():
    return os.path.dirname(os.path.realpath(sys.argv[0]))
"""
