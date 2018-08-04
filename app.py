"""
"""

import logging
from gettext import gettext as _

from we1schomp import browser, settings
from we1schomp.scrape import google, wordpress


def main():
    """
    """

    settings.load_from_yaml()
    config = settings.CONFIG
    sites = settings.SITES
    articles = []

    # Start logging.
    logfile = logging.FileHandler(config['LOG_FILE'])
    logfile.setFormatter(logging.Formatter(config['LOG_FILE_FORMAT']))
    console_log = logging.StreamHandler()
    console_log.setFormatter(logging.Formatter(config['LOG_CONSOLE_FORMAT']))
    logging.basicConfig(level=logging.INFO, handlers=[logfile, console_log])
    log = logging.getLogger(__name__)

    # Get all sites not flagged "skip". If all sites are flagged, we're done!
    sites = [s for s in sites if not s.get('skip', False)]

    # WordPress Scrape
    articles = wordpress.scrape(sites)
    config['ENABLE_WORDPRESS'] = False
    settings.save_to_yaml()

    ## Google Scrape
    #driver = browser.get_webdriver('http://harbor.english.ucsb.edu:4444/wd/hub')
    #articles = google.scrape(sites, driver)
    #driver.close()

    log.info(_('Done! Collected %d articles.'), len(articles))


if __name__ == '__main__':
    main()
