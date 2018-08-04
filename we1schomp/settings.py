# -*- coding: utf-8 -*-
""" Global configuration information & initialization functions.

WE1S Chomp <http://github.com/seangilleran/we1schomp>
A WhatEvery1Says project <http://we1s.ucsb.edu>
"""

import os
from gettext import gettext as _
from logging import getLogger

from ruamel.yaml import YAML

LOCAL_PATH = os.getenv('WE1S_LOCAL_PATH', 'local')
CONFIG_FILE = os.getenv('WE1S_CONFIG_FILE', 'settings.yaml')
SITES_FILE = os.getenv('WE1S_SITES_FILE', 'sites.yaml')

CONFIG = {}
SITES = []


def load_from_yaml():
    """ Load the settings and sites files from YAML.
    """

    global CONFIG  # pylint: disable=W0603
    global SITES  # pylint: disable=W0603

    # No logging yet since we've yet to load the log settings.

    config_filename = os.path.join(LOCAL_PATH, CONFIG_FILE)
    sites_filename = os.path.join(LOCAL_PATH, SITES_FILE)
    yaml = YAML()

    with open(config_filename, encoding='utf-8') as yaml_file:
        config = yaml.load(yaml_file)
    CONFIG = config

    with open(sites_filename, encoding='utf-8') as yaml_file:
        for site in yaml.load_all(yaml_file):
            SITES.append(site)

    if not os.path.exists(config['FILE_OUTPUT_PATH']):
        os.makedirs(config['FILE_OUTPUT_PATH'])


def save_to_yaml():
    """ Saves the settings and sites files to YAML.

    Returns:
        bool: True if successful.
    """

    log = getLogger(__name__)
    config_filename = os.path.join(LOCAL_PATH, CONFIG_FILE)
    sites_filename = os.path.join(LOCAL_PATH, SITES_FILE)
    yaml = YAML()

    log.info(_('Saving settings: %s'), config_filename)
    with open(config_filename, 'w') as yaml_file:
        yaml.dump(CONFIG, yaml_file)

    log.info(_('Saving sites: %s'), sites_filename)
    with open(sites_filename, 'w') as yaml_file:
        yaml.dump_all(SITES, yaml_file)

    return True
