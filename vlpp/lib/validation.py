# -*- coding: utf-8 -*-


from jsonmerge import merge
import os
from .utils import APP_DIR, load_json, pet_type, write_json


class Validation(object):

    def __init__(self, args):
        self.config_file = os.path.abspath(args.config_file)
        self.arguments = load_json(self.config_file)['arguments']
        self.config_dict = self.set_config_dict()

    @property
    def _pet_dir(self):
        """Return absolute path of the pet directory
        """
        if 'pet_dir' in self.arguments:
            return self.arguments['pet_dir']
        else:
            #TODO: print warning
            pass

    @property
    def _fs_dir(self):
        """Return absolute path of the freesurfer directory
        """
        if 'fs_dir' in self.arguments:
            return self.arguments['fs_dir']
        else:
            #TODO: print warning
            pass

    @property
    def _participant_id(self):
        """Return participant id
        """
        if 'participant_id' in self.arguments:
            return self.arguments['participant_id']
        else:
            #TODO: print warning
            pass

    @property
    def _base_dir(self):
        return os.path.dirname(os.path.dirname(self.config_file))

    @property
    def _output_dir(self):
        """Return absolute path of the output
        """
        if 'output_dir' in self.arguments:
            output_dir = self.arguments['output_dir']
            return os.path.join(
                    os.path.abspath(output_dir),
                    self._participant_id,
                    )
        else:
            return os.path.join(
                    self._base_dir,
                    'output',
                    self._participant_id,
                    )

    @property
    def _working_dir(self):
        """Return absolute path of working directory
        """
        if 'working_dir' in self.arguments:
            working_dir = self.arguments['working_dir']
            return os.path.join(
                    os.path.abspath(working_dir),
                    self._participant_id,
                    )
        else:
            return os.path.join(
                    self._base_dir,
                    'working_dir',
                    self._participant_id,
                    )

    def set_config_dict(self):
        """Return a configuration dictionnary
        Load the default dictionnary from config_default.json file and update it
        """
        defaultConfigFile = os.path.join(
                APP_DIR, 'config', 'config_default.json')
        defaultConfig = load_json(defaultConfigFile)

        studyConfigFile = os.path.join(self._base_dir, "code", "config.json")
        if os.path.exists(studyConfigFile):
            studyConfig = merge(defaultConfig, load_json(studyConfigFile))
        else:
            studyConfig = defaultConfig

        subjectConfig = {
                "arguments": {
                    "pet_dir": self._pet_dir,
                    "fs_dir": self._fs_dir,
                    "participant_id": self._participant_id,
                    "output_dir": self._output_dir,
                    "working_dir": self._working_dir,
                    },
                "preparation": pet_type(os.path.join(
                        self._pet_dir, studyConfig["selectfiles"]["pet"]))
                }

        return merge(studyConfig, subjectConfig)

