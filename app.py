"""
"""

import logging
from gettext import gettext as _

from we1schomp import browser, config
from we1schomp.scrape import google, wordpress


def main():
    """
    """

    config.load_settings_from_yaml()
    config.load_sites_from_yaml()
    
    logging.basicConfig(level=logging.INFO)
    log = logging.getLogger(__name__)
    config = settings.CONFIG
    sites = config.SITES
    articles = []

    # Get all sites not flagged "skip". If all sites are flagged, we're done!
    sites = [s for s in sites if not s.get('skip', False)]

    # WordPress Scrape
    articles = wordpress.scrape(sites)
    config['ENABLE_WORDPRESS'] = False
    config.save_config_to_yaml()

    ## Google Scrape
    #driver = browser.get_webdriver('http://harbor.english.ucsb.edu:4444/wd/hub')
    #articles = google.scrape(sites, driver)
    #driver.close()

    log.info(_('Done! Collected %d articles.'), len(articles))


if __name__ == '__main__':
    main()
