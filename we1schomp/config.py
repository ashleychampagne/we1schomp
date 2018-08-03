# -*- coding: utf-8 -*-
""" Global configuration information.
"""

import os
from gettext import gettext as _
from logging import getLogger

from ruamel.yaml import YAML

SETTINGS_PATH = 'local'
SETTINGS_FILE = 'settings.yaml'
SITES_FILE = 'sites.yaml'


class Config:
    """
    """

    __config = []

    def __init__(self):
        if self.__config == []:
            self.load_config_from_yaml()

    def __getitem__(self, key):
        return self.__config[key]

    def __setitem__(self, key, value):
        self.__config.update({key: value})

    def load_config_from_yaml(self):
        """ Load the configuration file from YAML.
        """

        log = getLogger(__name__)
        yaml = YAML()

        filename = os.path.join(SETTINGS_PATH, SETTINGS_FILE)

        log.info(_('Loading settings file: %s'), filename)
        with open(filename) as yaml_file:
            self.__config = yaml.load(yaml_file)

    def save_to_yaml(self):
        """ Saves the settings file to YAML.

        Returns:
            bool: True if successful.
        """

        log = getLogger(__name__)
        yaml = YAML()

        filename = os.path.join(SETTINGS_PATH, SETTINGS_FILE)

        log.info(_('Saving settings: %s'), filename)
        with open(filename, 'w') as yaml_file:
            yaml.dump(self.__config, yaml_file)
        return True


class Sites:
    """
    """

    __sites = []

    def __init__(self):
        if self.__sites == []:
            self.load_sites_from_yaml()

    def __getitem__(self, key):
        return self.__sites[key]

    def load_sites_from_yaml(self):
        """ Load the sites file from YAML.
        """

        log = getLogger(__name__)
        yaml = YAML()

        filename = os.path.join(SETTINGS_PATH, SITES_FILE)

        log.info(_('Loading sites file: %s'), filename)
        with open(filename) as yaml_file:
            self.__sites = list(yaml.load_all(yaml_file))

    def save_to_yaml(self):
        """ Saves the sites file to YAML.

        Returns:
            bool: True if successful.
        """

        log = getLogger(__name__)
        yaml = YAML()

        filename = os.path.join(SETTINGS_PATH, SITES_FILE)

        log.info(_('Saving sites: %s'), filename)
        with open(filename, 'w') as yaml_file:
            yaml.dump_all(self.__sites, yaml_file)
        return True
