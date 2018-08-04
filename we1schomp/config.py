# -*- coding: utf-8 -*-
""" Global configuration information.
"""

import os
from gettext import gettext as _
from logging import getLogger

from ruamel.yaml import YAML

LOCAL_PATH = 'local'
SETTINGS_FILE = 'settings.yaml'
SITES_FILE = 'sites.yaml'

SETTINGS = dict()
SITES = list()


def load_settings_from_yaml():
    """
    """

    global SETTINGS
    yaml = YAML()
    filename = os.path.join(LOCAL_PATH, SETTINGS_FILE)

    with open(filename) as yaml_file:
        config = yaml.load(yaml_file)
    SETTINGS = config

    if not os.path.exists(SETTINGS['FILE_OUTPUT_PATH']):
        os.makedirs(SETTINGS['FILE_OUTPUT_PATH'])


def load_sites_from_yaml():
    """ Load the sites file from YAML.
    """

    global SITES
    yaml = YAML()
    filename = os.path.join(LOCAL_PATH, SITES_FILE)

    SITES = []
    with open(filename) as yaml_file:
        for site in yaml.load_all(yaml_file):
            SITES.append(site)


def save_config_to_yaml():
    """ Saves the settings file to YAML.

    Returns:
        bool: True if successful.
    """

    log = getLogger(__name__)
    yaml = YAML()
    filename = os.path.join(LOCAL_PATH, SETTINGS_FILE)

    log.info(_('Saving settings: %s'), filename)
    with open(filename, 'w') as yaml_file:
        yaml.dump(SETTINGS, yaml_file)
    return True


def save_sites_to_yaml():
    """ Saves the sites file to YAML.

    Returns:
        bool: True if successful.
    """

    log = getLogger(__name__)
    yaml = YAML()
    filename = os.path.join(LOCAL_PATH, SITES_FILE)

    log.info(_('Saving sites: %s'), filename)
    with open(filename, 'w') as yaml_file:
        yaml.dump_all(SITES, yaml_file)
    return True
