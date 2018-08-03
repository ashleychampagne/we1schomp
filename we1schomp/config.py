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


def load_config_from_yaml():
    """
    """

    log = getLogger(__name__)
    yaml = YAML()
    global CONFIG

    filename = os.path.join(SETTINGS_PATH, SETTINGS_FILE)

    log.info(_('Loading settings file: %s'), filename)
    with open(filename) as yaml_file:
        CONFIG = yaml.load(yaml_file)


def load_sites_from_yaml():
    """ Load the sites file from YAML.
    """

    log = getLogger(__name__)
    yaml = YAML()
    global SITES

    filename = os.path.join(SETTINGS_PATH, SITES_FILE)

    log.info(_('Loading sites file: %s'), filename)
    with open(filename) as yaml_file:
        SITES = list(yaml.load_all(yaml_file))


def save_config_to_yaml():
    """ Saves the settings file to YAML.

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

    Returns:
        bool: True if successful.
    """

    log = getLogger(__name__)
    yaml = YAML()

    filename = os.path.join(SETTINGS_PATH, SITES_FILE)

    log.info(_('Saving sites: %s'), filename)
    with open(filename, 'w') as yaml_file:
        yaml.dump_all(SITES, yaml_file)
    return True
