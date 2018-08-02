# -*- coding: utf-8 -*-
""" Common browser/web tools.
"""

import json
import random
import time
import urllib
from gettext import gettext as _
from logging import getLogger
from urllib.request import urlopen

from bs4 import BeautifulSoup


def sleep(config=None, short=False, seconds=0.0):
    """ Pause execution for a short time.

    Args:
        config (dict): Configuration settings, including a min and max time.
        short (boolean): Set to True to always pick the min sleep time.
        seconds (float): Sleep for a specific number of seconds.
    """

    log = getLogger(__name__)

    if seconds == 0.0:

        if config is not None:
            seconds_min = config['WEBDRIVER_SLEEP_MIN']
            seconds_max = config['WEBDRIVER_SLEEP_MAX']

            if not short:
                seconds = random.uniform(seconds_min, seconds_max)
            else:
                seconds = seconds_min

    log.debug(_('Sleeping for %.02f seconds.'), seconds)
    time.sleep(seconds)


def get_json_from_url(url):
    """ Return JSON data from a URL.
    """

    log = getLogger(__name__)

    log.debug(_('Getting JSON from: %s'), url)
    try:
        with urlopen(url) as response:
            json_data = json.loads(response.read())
    except (urllib.error.HTTPError, urllib.error.URLError) as e:
        log.debug(_('URLLib Error: %s'), e)
        log.debug(_('No data collected.'))
        json_data = None

    return json_data


def get_soup_from_url(url, config, webdriver=None, force_selenium=False):
    """ Get BeautifulSoup data from a URL.

    Args:
        url (str): URL to get.
        config (dict): Configuration information.
        webdriver (WebDriver): Selenium webdriver.
        force_selenium (boolean): Use Selenium first. Otherwise prefer URLLib.
    
    Raises:
        AssertionError: If you want to use a webdriver, you must pass one!

    Returns:
        BeautifulSoup: D.O.M. data.
    """

    log = getLogger(__name__)

    if not webdriver and force_selenium:
        raise AssertionError(_('Cannot force webdriver when no webdriver passed!'))

    if not webdriver or force_selenium:
        try:
            with urlopen(url) as result:
                log.info(_('URLLib: %s'), url)
                soup = BeautifulSoup(result.read(), 'html5lib')
                return soup
        except (urllib.error.HTTPError, urllib.error.URLError) as e:
            log.debug(_('URLLib Error: %s'), e)

    assert webdriver is not None
    log.info(_('Selenium: %s'), url)
    soup = BeautifulSoup(webdriver.page_source, 'html5lib')
    return soup



def captcha_check(url, config):
    """ Check for a CAPTCHA and wait for intervention.
    """

    log = getLogger(__name__)

    if '/sorry/' in url:
        log.error(_('CAPTCHA detected! Waiting for human...'))

        # Pause here...
        while '/sorry/' in url:
            sleep(config, short=True)
        
        log.info(_('Ok!'))
        sleep(config)
