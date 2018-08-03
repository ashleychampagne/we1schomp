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

CONFIG = dict()
SITES = list()


def load_config_from_yaml():
    """
    """

    global CONFIG
    yaml = YAML()
    filename = os.path.join(LOCAL_PATH, SETTINGS_FILE)

    with open(filename) as yaml_file:
        config = yaml.load(yaml_file)
    CONFIG = config

    CONFIG['FILE_OUTPUT_PATH'] = os.path.join(LOCAL_PATH, CONFIG['FILE_OUTPUT_PATH'])
    if not os.path.exists(CONFIG['FILE_OUTPUT_PATH']):
        os.makedirs(CONFIG['FILE_OUTPUT_PATH'])


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
        yaml.dump(CONFIG, yaml_file)
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
