# -*- coding: utf-8 -*-
""" Global configuration information.
"""

import os
from gettext import gettext as _
from logging import getLogger

from ruamel.yaml import YAML


default_config = dict(

    # Default queries/terms to use in searches.
    QUERIES=[  # Per-site (overrides this setting): queries[]
        'humanities',
        'liberal arts'
    ],

    # WordPress settings.
    WORDPRESS_ENABLE=True,  # Per-site: wpEnable
    WORDPRESS_GET_PAGES=True,  # Per-site: wpPagesEnable
    WORDPRESS_GET_POSTS=True,  # Per-site: wpPostsEnable
    WORDPRESS_API_URL='/wp-json/wp/v2/',
    WORDPRESS_PAGES_QUERY_URL='{api_url}pages?search={query}&sentence=1',
    WORDPRESS_POSTS_QUERY_URL='{api_url}posts?search={query}&sentence=1',

    # Google/direct scrape settings.
    GOOGLE_SEARCH_ENABLE=True,  # Per-site: googleSearchEnable
    GOOGLE_SCRAPE_ENABLE=True,  # Per-site: googleScrapeEnable
    GOOGLE_QUERY_URL='http://google.com/search?q="{query}"+site%3A{site}&safe=off&filter=0',
    GOOGLE_CONTENT_TAG='p',  # Per-site (overrides this setting): googleContentTag
    GOOGLE_CONTENT_LENGTH_MIN=75,  # Per-site (overrides this setting): googleContentLengthMin
    GOOGLE_URL_STOPWORDS=[  # Per-site (overrides this setting): googleURLStopwords
        'keyword',
        'author',
        'biography',
        'contributor',
        'tag/',
        'tags/',
        'tool/',
        'forum.',
        'forums.',
        'comment/',
        'comment.',
        'comments.',
        '.pdf',
        '.docx',
        '.doc',
        '/el/',
        '/es/',
        '/fr/',
        '/de/'
    ],

    # Metadata settings.
    DB_NAME_FORMAT='we1schomp_{query}_{site}_{slug}',
    DB_METAPATH='Corpus,{site},Rawdata',
    DB_NAMESPACE='we1sv2.0',

    # Regex processing. Experimental!
    # This looks for:
    # - URL strings, common in blog posts, etc., and probably not useful for
    #   topic modelling.
    # - Irregular punctuation, i.e. punctuation left over from formatting
    #   or HTML symbols that Bleach missed.
    REGEX_ENABLE = True,
    REGEX_STRING = r'http(.*?)\s|[^a-zA-Z0-9\s\.\,\!\"\'\-\:\;\(\)\p{Sc}]',

    # Path settings.
    FILENAME_FORMAT='we1schomp_{query}_{site}_{timestamp}_{index}.json',
    FILE_OUTPUT_PATH=os.path.join(os.getcwd(), 'local', 'output'),
    SETTINGS_FILE=os.path.join('local', 'settings.yaml'),
    SITES_FILE=os.path.join('local', 'sites.yaml'),

    # Logging settings.
    LOG_FILE='we1schomp.log',
    LOG_FORMAT='%(asctime)s - %(name)s - %(levelname)s: %(message)s',
    CONSOLE_FORMAT='%(levelname)s: %(message)s',

    # Selenium WebDriver settings.
    WEBDRIVER_URL=os.getenv('WE1S_WEBDRIVER_URL'),
    WEBDRIVER_SLEEP_MIN=0.5,
    WEBDRIVER_SLEEP_MAX=5.0
)


default_sites = [
    dict(
        name='WhatEvery1Says',
        slug='we1s',
        site='we1s.ucsb.edu',
        skip=True
    ),
    dict(
        name='The Anarcho-Syndicalist Review',
        slug='anarcho-syndicalist-review',
        site='syndicalist.us'
    )
]


def load_from_yaml(filename_settings, filename_sites):
    """ Load sites & settings from YAML files.

    Args:
        filename_settings (str): Settings YAML file path.
        filename_sites (str): Sites YAML file path.
    
    Returns:
        (dict, dict): settings, sites.

    Raises:
        FileNotFoundError: Use default settings.
    """

    log = getLogger(__name__)
    yaml = YAML()
    filename_settings = os.path.join('local', filename_settings)
    filename_sites = os.path.join('local', filename_sites)

    try:
        with open(filename_settings) as yamlfile:
            settings = yaml.load(yamlfile)
        settings.update({'SETTINGS_FILE': 'local/settings_out.yaml'})
        log.info(_('Loading settings file: %s'), filename_settings)
    except FileNotFoundError:
        settings = default_config
        log.error(_('Settings file not found: %s'), filename_settings)
        log.warning(_('Using default settings.'))
    
    try:
        with open(filename_sites) as yamlfile:
            sites = list(yaml.load_all(yamlfile))
        settings.update({'SITES_FILE': 'local/sites_out.yaml'})
        log.info(_('Loading sites file: %s'), filename_sites)
    except FileNotFoundError:
        sites = default_sites
        log.error(_('Sites file not found: %s'), filename_sites)
        log.warning(_('Using default sites.'))

    # Make settings dir if necessary.
    if not os.path.exists(settings['FILE_OUTPUT_PATH']):
        log.info(_('Creating output directory: %s'), settings['FILE_OUTPUT_PATH'])
        os.makedirs(settings['FILE_OUTPUT_PATH'])

    return settings, sites


def save_to_yaml(settings, sites):
    """ Save current sites & settings values to YAML files.

    Args:
        settings (dict): Settings values.
        sites (dict): Sites.
    
    Returns:
        boolean: True for success.
    
    TODO:
        * Exception handling.
    """

    log = getLogger(__name__)
    yaml = YAML()
    filename_settings = settings['SETTINGS_FILE']
    filename_sites = settings['SITES_FILE']

    log.info(_('Saving settings: %s'), filename_settings)
    with open(filename_settings, 'w') as yamlfile:
        yaml.dump(settings, yamlfile)

    log.info(_('Saving sites: %s'), filename_sites)
    with open(filename_sites, 'w') as yamlfile:
        yaml.dump_all(sites, yamlfile)

    log.info(_('Ok!'))
    return True
