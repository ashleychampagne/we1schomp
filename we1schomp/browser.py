# -*- coding: utf-8 -*-
""" Common browser/web tools.
"""

import json
import random
import time
from gettext import gettext as _
from logging import getLogger
from urllib import error
from urllib.request import urlopen

from bs4 import BeautifulSoup
from selenium import webdriver

from we1schomp import config


def get_webdriver(grid_url):
    """ Get a handle to the Selenium webdriver or make a new one.
    """

    capabilities = webdriver.DesiredCapabilities.CHROME
    __webdriver = webdriver.Remote(
        desired_capabilities=capabilities, command_executor=grid_url)

    return __webdriver


def sleep(short=False, seconds=0.0):
    """ Pause execution for a short time.

    Args:
        short (boolean): Set to True to always pick the min sleep time.
        seconds (float): Sleep for a specific number of seconds.
    """

    log = getLogger(__name__)
    CONFIG = config.SETTINGS

    if seconds == 0.0:
        seconds_min = CONFIG['WEBDRIVER_SLEEP_MIN']
        seconds_max = CONFIG['WEBDRIVER_SLEEP_MAX']

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
            return json.loads(response.read())
    except (error.HTTPError, error.URLError) as ex:
        log.debug(_('URLLib Error: %s'), ex)
        log.debug(_('No data collected.'))
    except json.decoder.JSONDecodeError as ex:
        log.warning(_('JSON Error: %s'), ex)
        log.warning(_('No data collected.'))

    return None


def get_soup_from_url(url):
    """ Get BeautifulSoup data from a URL using URLLib.urlopen().

    Thread-safe, but blocked by some sites.
    """

    log = getLogger(__name__)

    # Just in case...
    url = url.replace('http://', '').replace('https://', '')
    url = f'http://{url}'

    try:
        with urlopen(url) as result:
            log.info(_('URLLib: %s'), url)
            soup = BeautifulSoup(result.read(), 'html5lib')
            return soup
    except (error.HTTPError, error.URLError) as ex:
        log.debug(_('URLLib Error: %s'), ex)
        return None


def get_soup_from_selenium(url, driver):
    """Get BeautifulSoup data from a URL using webdriver.get().

    Not thread-safe, but more versatile than get_soup_from_url().
    Also required if there is a potential for CAPTCHAs.
    """

    log = getLogger(__name__)

    log.info(_('Selenium: %s'), url)
    driver.get(url)

    # Check for a CAPTCHA.
    if '/sorry/' in driver.current_url:
        log.error(_('CAPTCHA detected! Waiting for human...'))

        # Pause here...
        while '/sorry/' in driver.current_url:
            sleep(short=True)

        log.info(_('Ok!'))
        sleep()

    soup = BeautifulSoup(driver.page_source, 'html5lib')
    log.debug(_('Soup: %s'), soup)
    return soup
