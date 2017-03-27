# -*- coding: utf-8 -*-


import os
from . import utils


class Validation(object):

    def __init__(self, args):
        self._args = args
        self.userConfig = utils.load_json(args.config_file)
        self.userArguments = self.userConfig['arguments']

    @property
    def _pet_dir(self):
        """Return absolute path of the pet directory
        """
        if 'pet_dir' in self.userArguments:
            pet_dir = self.userArguments['pet_dir']
            return os.path.abspath(pet_dir)
        else:
            #TODO
            pass

    @property
    def _fs_dir(self):
        """Return absolute path of the freesurfer directory
        """
        if 'fs_dir' in self.userArguments:
            fs_dir = self.userArguments['fs_dir']
            return os.path.abspath(fs_dir)
        else:
            #TODO
            pass

    @property
    def _subject_id(self):
        """Return subject id
        """
        if 'subject_id' in self.userArguments:
            return self.userArguments['subject_id']
        else:
            return os.path.basename(self._pet_dir)

    @property
    def _output_dir(self):
        """Return absolute path of the output
        """
        if 'output_dir' in self.userArguments:
            output_dir = self.userArguments['output_dir']
            return os.path.join(
                    os.path.abspath(output_dir),
                    self._subject_id,
                    )
        else:
            #TODO
            pass

    @property
    def _working_dir(self):
        """Return absolute path of working directory
        """
        if 'working_dir' in self.userArguments:
            working_dir = self.userArguments['working_dir']
        else:
            working_dir = os.path.join(os.environ['SCRATCH'])

        return os.path.join(
                os.path.abspath(working_dir),
                self._subject_id,
                )

    @property
    def _debug(self):
        return self._args.debug

    @property
    def config_dict(self):
        """Return a configuration dictionnary
        Load the default dictionnary from config_default.json file and update it
        """
        defaultConfigFile = os.path.join(
                utils.PROD_DIR, 'config', 'config_default.json')
        defaultConfig = utils.load_json(defaultConfigFile)

        arguments = {}
        arguments["pet_dir"] = self._pet_dir
        arguments["fs_dir"] = self._fs_dir
        arguments["subject_id"] = self._subject_id
        arguments["output_dir"] = self._output_dir
        arguments["working_dir"] = self._working_dir
        arguments["debug"] = self._debug

        self.userConfig.update({"arguments": arguments})
        defaultConfig.update(self.userConfig)

        return defaultConfig

