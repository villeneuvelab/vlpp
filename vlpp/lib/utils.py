# -*- coding: utf-8 -*-


import glob
import json
import os


PIPELINENAME = 'VLPP'
APP_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


# Helper

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

def pet_type(globInput):
    pet = glob.glob(globInput)

    #extension
    base, ext = os.path.splitext(pet[0])
    if ext == '.gz':
        ext = '{}{}'.format(os.path.splitext(base)[1], ext)
    ext = ext[1:]

    if len(pet) == 1:
        pass

    return {"ext": ext}


# Class
from nipype.interfaces.utility import IdentityInterface
from nipype.pipeline.engine import Node

class WorkflowManager(object):

    def __init__(self, config, name):
        self._config = config
        self._name = name
        self._inputnode = None
        self._outputnode = None
        self._wf = None
        self.setnodes()
        #self.infields = None
        #self.outfields = None

    def setnodes(self):
        self._inputnode = Node(
                IdentityInterface(fields=self.infields), 'inputnode')
        self._outputnode = Node(
                IdentityInterface(fields=self.outfields), 'outputnode')

    @property
    def config(self):
        return self._config

    @property
    def name(self):
        return self._name.title()

    @property
    def wf(self):
        if self.ignore:
            return None
        else:
            self.generate()
            return self._wf

    @property
    def kind(self):
        if 'kind' in self._config:
            return self._config['kind']
        else:
            return 'default'

    @property
    def inputnode(self):
        return self._inputnode

    @property
    def outputnode(self):
        return self._outputnode

    def generate(self):
        """
        Should be overwrite by the child and generate self._wf
        """
        raise NotImplementedError

    def error(self):
        #TODO implement this function with nipype error or logging ?
        msg = "'{}' is not implemented for the {} workflow"
        print(msg.format(self.kind, self.name))

    @property
    def ignore(self):
        """
        User can ignore a workflow when the key "ignore" is set to "True"
        """
        if 'ignore' in self._config:
            value = self._config['ignore']
            if isinstance(value, bool):
                return value
            else:
                msg = "'{}' is not `bool`, workflow {} will be implemented"
                print(msg.format(value, self.name))
                return False
        else:
            return False

