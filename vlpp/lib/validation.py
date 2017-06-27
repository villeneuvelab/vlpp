# -*- coding: utf-8 -*-


from jsonmerge import merge
import glob
import os
import sys
from .utils import APP_DIR, load_json


class Validation(object):

    def __init__(self, args):
        self.pet_dir = self._pet_dir(args.pet_dir)
        self.participant_id = self._participant_id(args.participant_id)
        self.fs_dir = self._fs_dir(args.fs_dir)
        self.output_dir = self._output_dir(args.output_dir)
        self.working_dir = self._working_dir()

        if args.config_file:
            self.argsConfig = load_json(args.config_file)
        else:
            self.argsConfig = {}
        self.config_dict = self._config_dict()


    def _pet_dir(self, pet_dir):
        """
        Check if pet_dir exist and return absolute path
        """
        if os.path.exists(pet_dir):
            return os.path.abspath(pet_dir)
        else:
            sys.exit("Directory does not exist: {}".format(pet_dir))


    def _participant_id(self, id):
        """
        Return participant_id, if not set it returns the pet directory name
        """
        if id:
            return id
        else:
            return os.path.basename(os.path.normpath(self.pet_dir))


    def _fs_dir(self, fs_dir):
        """
        Check if fs_dir exist and return absolute path
        If no fs_dir was provided by the user, the function guess that fs_dir is
        a directory named "freesurfer" inside pet_dir.
        """
        if fs_dir:
            if os.path.exists(fs_dir):
                return os.path.abspath(fs_dir)
            else:
                sys.exit("Directory does not exist: {}".format(fs_dir))
        else:
            print("No freesurfer directory was provided")
            guess = os.path.join(self.pet_dir, "freesurfer")
            if os.path.exists(guess):
                print("Freesurfer directory found: {}".format(guess))
                return guess
            else:
                sys.exit("No freesurfer directory found")


    def _output_dir(self, output_dir):
        """
        Return absolute path of the output
        """
        if output_dir:
            return os.path.join(os.path.abspath(output_dir), self.participant_id)
        else:
            return os.path.join(os.getcwd(), 'output', self.participant_id)


    def _working_dir(self):
        """
        Return absolute path of working directory
        """
        return os.path.join(
                os.getcwd(), 'output', 'working_dir', self.participant_id)


    def _config_dict(self):
        """
        Return a configuration dictionnary
        Load the default dictionnary from config_default.json file and update it
        """
        defaultConfigFile = os.path.join(APP_DIR, 'config', 'config_default.json')
        defaultConfig = load_json(defaultConfigFile)

        studyConfigFile = os.path.join(os.getcwd(), "code", "config.json")
        if os.path.exists(studyConfigFile):
            studyConfig = merge(defaultConfig, load_json(studyConfigFile))
        else:
            studyConfig = defaultConfig

        config_dict = merge(studyConfig, self.argsConfig)

        subjectConfig = {
                "arguments": {
                    "pet_dir": self.pet_dir,
                    "fs_dir": self.fs_dir,
                    "participant_id": self.participant_id,
                    "output_dir": self.output_dir,
                    "working_dir": self.working_dir,
                    },
                "preparation": self._pet_type(studyConfig["selectfiles"]["pet"])
                }

        return merge(config_dict, subjectConfig)


    def _pet_type(self, selectfiles):
        """
        """
        globInput = os.path.join(self.pet_dir, selectfiles)
        pet = glob.glob(globInput)

        num = len(pet)
        if num == 0:
            msg = "No pet images were found with this parser: {}"
            sys.exit(msg.format(globInput))
        elif num == 1:
            size = "one"
        else:
            size = "several"

        #extension
        base, ext = os.path.splitext(pet[0])
        if ext == '.gz':
            ext = '{}{}'.format(os.path.splitext(base)[1], ext)
        ext = ext[1:]

        return {
                "file": size,
                "ext": ext,
                }

