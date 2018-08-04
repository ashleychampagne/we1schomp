# -*- coding: utf-8 -*-
""" Common browser/web tools.

WE1S Chomp <http://github.com/seangilleran/we1schomp>
A WhatEvery1Says project <http://we1s.ucsb.edu>
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
from selenium.webdriver.common.keys import Keys

from we1schomp import settings


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
        seconds (float): Sleep for a specific number of seconds. Overrides
            other settings.
    """

    log = getLogger(__name__)
    config = settings.CONFIG

    if seconds == 0.0:
        seconds_min = config['WEBDRIVER_SLEEP_MIN']
        seconds_max = config['WEBDRIVER_SLEEP_MAX']

        if not short:
            seconds = random.uniform(seconds_min, seconds_max)
        else:
            seconds = seconds_min

    log.debug(_('Sleeping for %.02f seconds.'), seconds)
    time.sleep(seconds)


def get_json_from_url(url):
    """ Return JSON data from a URL, None if load failed.
    """

    log = getLogger(__name__)

    log.debug(_('Getting JSON from: %s'), url)
    try:
        with urlopen(url) as response:
            return json.loads(response.read())

    except (error.HTTPError, error.URLError) as ex:
        log.debug(_('URLLib Error, no data collected.: %s'), ex)
    except json.decoder.JSONDecodeError as ex:
        log.warning(_('JSON Error, no data collected: %s'), ex)
    return None


def get_soup_from_url(url):
    """ Get BeautifulSoup data from a URL using URLLib.urlopen().

    Fast, but blocked by some sites.
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


def get_soup_from_selenium(url, driver, use_new_tab=False):
    """Get BeautifulSoup data from a URL using webdriver.get().

    Slow, but more versatile than get_soup_from_url().
    """

    log = getLogger(__name__)

    log.info(_('Selenium: %s'), url)

    if use_new_tab:
        driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + 't')
        sleep(short=True)

    driver.get(url)

    # Check for a CAPTCHA.
    if '/sorry/' in driver.current_url:
        log.error(_('CAPTCHA detected! Waiting for human...'))

        # Pause here...
        while '/sorry/' in driver.current_url:
            sleep(short=True)

        log.info(_('CAPTCHA cleared.'))
        sleep()

    soup = BeautifulSoup(driver.page_source, 'html5lib')

    if use_new_tab:
        driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL, 'w')

    return soup
