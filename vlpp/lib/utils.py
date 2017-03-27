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


def print_json(data, msg=None):
    print
    if msg != None: print(msg)
    print(json.dumps(data, indent=4))
    print

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
        if 'kind' in self._config:
            return self._config['kind']
        else:
            return 'default'

    @property
    def ignore(self):
        if 'ignore' in self._config:
            return self._config['ignore']
        else:
            return False

    @property
    def wf(self):
        return self._wf

    def generate(self):
        raise NotImplementedError

    def connect(self, main_wf):
        raise NotImplementedError

    def implement(self, main_wf):
        self.generate()
        self.connect(main_wf)

    def implement_error(self):
        #TODO implement this function with nipype error or logging ?
        msg = "'{}' is not implemented for the {} workflow"
        print(msg.format(self.kind, self.name))

