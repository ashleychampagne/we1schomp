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

from selenium import webdriver
from bs4 import BeautifulSoup

from we1schomp.config import config


def get_webdriver():
    """ Get a handle to the Selenium webdriver or make a new one.
    """

    grid_url = config['WEBDRIVER_URL']
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
    """ Return JSON data from a URL.
    """

    log = getLogger(__name__)

    log.debug(_('Getting JSON from: %s'), url)
    try:
        with urlopen(url) as response:
            return json.loads(response.read())
    except (urllib.error.HTTPError, urllib.error.URLError) as e:
        log.debug(_('URLLib Error: %s'), e)
        log.debug(_('No data collected.'))
    except json.decoder.JSONDecodeError as e:
        log.warning(_('JSON Error: %s'), e)
        log.warning(_('No data collected.'))

    return None


def get_soup_from_url(url):
    """ Get BeautifulSoup data from a URL.

    Args:
        url (str): URL to get.
        webdriver (WebDriver): Selenium webdriver.
        force_selenium (boolean): Use Selenium first. Otherwise prefer URLLib.
    
    Raises:
        AssertionError: If you want to use a webdriver, you must pass one!

    Returns:
        BeautifulSoup: D.O.M. data.
    """

    log = getLogger(__name__)

    # Just in case...
    url = url.replace('http://', '').replace('https://','')
    url = f'http://{url}'

    try:
        with urlopen(url) as result:
            log.info(_('URLLib: %s'), url)
            soup = BeautifulSoup(result.read(), 'html5lib')
            return soup
    except (urllib.error.HTTPError, urllib.error.URLError) as e:
        log.debug(_('URLLib Error: %s'), e)
        return None


def get_soup_from_selenium(url, webdriver):

    log = getLogger(__name__)

    log.info(_('Selenium: %s'), url)
    webdriver.get(url)
    soup = BeautifulSoup(webdriver.page_source, 'html5lib')
    log.debug(_('Soup: %s'), soup)
    return soup



def captcha_check(url):
    """ Check for a CAPTCHA and wait for intervention.
    """

    log = getLogger(__name__)

    if '/sorry/' in url:
        log.error(_('CAPTCHA detected! Waiting for human...'))

        # Pause here...
        while '/sorry/' in url:
            sleep(short=True)
        
        log.info(_('Ok!'))
        sleep()
