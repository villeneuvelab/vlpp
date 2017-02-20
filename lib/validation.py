# -*- coding: utf-8 -*-


import os
from lib import utils


class Validation(object):

    def __init__(self, args):
        self._args = args

    @property
    def _input_dir(self):
        """Return absolute path of the input
        """
        return os.path.abspath(self._args.input_dir)

    @property
    def _subject_id(self):
        """Return subject id
        """
        return os.path.basename(self._input_dir)

    @property
    def _output_dir(self):
        """Return absolute path of the output
        """
        return os.path.join(
                os.path.abspath(self._args.output_dir),
                self._subject_id,
                )

    @property
    def _working_dir(self):
        """Return absolute path of working directory
        """
        wd = self._args.working_dir
        if wd == None:
            wd = os.path.join(os.environ['SCRATCH'])
        return os.path.join(
                os.path.abspath(wd),
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
        defaultDict = utils.load_json(defaultConfigFile)

        if self._args.config_file == None:
            userDict = {}
        else:
            userDict = utils.load_json(self._args.config_file)

        # Arguments dictionnary
        argsDict = {}
        argsDict['input_dir'] = self._input_dir
        argsDict['subject_id'] = self._subject_id
        argsDict['output_dir'] = self._output_dir
        argsDict['working_dir'] = self._working_dir
        argsDict['debug'] = self._debug
        userDict.update({'arguments': argsDict})

        defaultDict.update(userDict)
        return defaultDict

