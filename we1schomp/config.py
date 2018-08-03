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

CONFIG = dict()
SITES = dict()


def load_config_from_yaml(filename=''):
    """ Load the configuration file from YAML.

    Args:
        filename (str): File to load. This will be added to SETTINGS_PATH,
            which can be changed in env. var. WE1SCHOMP_SETTINGS_PATH.

    Returns:
        dict: A copy of CONFIG.
    """

    log = getLogger(__name__)
    yaml = YAML()

    filename = os.path.join(SETTINGS_PATH, SETTINGS_FILE)

    log.info(_('Loading settings file: %s'), filename)
    with open(filename) as yaml_file:
        CONFIG = yaml.load(yaml_file)  # pylint: disable=W0621,C0103
    return CONFIG


def load_sites_from_yaml(filename=''):
    """ Load the sites file from YAML.

    Args:
        filename (str): File to load. This will be added to SETTINGS_PATH,
            which can be changed in env. var. WE1SCHOMP_SETTINGS_PATH.

    Returns:
        dict: A copy of SITES.
    """

    log = getLogger(__name__)
    yaml = YAML()

    filename = os.path.join(SETTINGS_PATH, SITES_FILE)

    log.info(_('Loading sites file: %s'), filename)
    with open(filename) as yaml_file:
        SITES = yaml.load(yaml_file)  # pylint: disable=W0621,C0103
    return SITES


def save_config_to_yaml():
    """ Saves the settings file to YAML.

    Filename is defined in load_settings_from_yaml() or by changing the env.
    var. WE1SCHOMP_SETTINGS_FILE.

    Returns:
        bool: True if successful.
    """

    log = getLogger(__name__)
    yaml = YAML()

    filename = os.path.join(SETTINGS_PATH, SETTINGS_FILE)

    log.info(_('Saving settings: %s'), filename)
    with open(filename, 'w') as yaml_file:
        yaml.dump(CONFIG, yaml_file)
    return True


def save_sites_to_yaml():
    """ Saves the sites file to YAML.

    Filename is defined in load_sites_from_yaml() or by changing the env.
    var. WE1SCHOMP_SITES_FILE.

    Returns:
        bool: True if successful.
    """

    log = getLogger(__name__)
    yaml = YAML()

    filename = os.path.join(SETTINGS_PATH, SITES_FILE)

    log.info(_('Saving sites: %s'), filename)
    with open(filename, 'w') as yaml_file:
        yaml.dump(SITES, yaml_file)
    return True
