"""
"""

import logging
from gettext import gettext as _
from multiprocessing.dummy import Pool as ThreadPool

from we1schomp import browser, config
from we1schomp.scrape import google, wordpress


def main():
    """
    """

    logging.basicConfig(level=logging.INFO)
    log = logging.getLogger(__name__)
    config.load_config_from_yaml()
    config.load_sites_from_yaml()
    driver = browser.get_webdriver('http://harbor.english.ucsb.edu:4444/wd/hub')

    while True:

        # Get all sites not flagged "skip". If all sites are flagged, we're done!
        sites = [s for s in config.SITES if not s.get('skip', False)]
        if sites == []:
            log.info(_('Queue finished. Goodbye!'))
            return

        # WordPress
        if config.CONFIG['WORDPRESS_ENABLE']:
            log.info(_('WordPress: Starting queue.'))

            pool = ThreadPool(config.CONFIG['THREAD_POOL_SIZE'])
            pool.map(wordpress.save_articles, sites)
            pool.close()
            pool.join()

            log.info(_('WordPress: Queue complete!'))
            config.CONFIG['WORDPRESS_ENABLE'] = False
            sites.save_to_yaml()
            config.save_config_to_yaml()
            continue

        # Google Search
        if config.CONFIG['GOOGLE_SEARCH_ENABLE']:
            log.info(_('Google Search: Starting queue.'))

            for site in sites:
                google.save_search_results(site, driver)

            log.info(_('Google Search: Queue complete!'))
            config.CONFIG['GOOGLE_SEARCH_ENABLE'] = False
            sites.save_sites_to_yaml()
            config.save_config_to_yaml()
            continue

        # Google Scrape
        if config.CONFIG['GOOGLE_SCRAPE_ENABLE']:
            log.info(_('Google Scrape: Starting queue.'))

            pool = ThreadPool(config.CONFIG['THREAD_POOL_SIZE'])
            pool.map(google.save_articles, sites)
            pool.close()
            pool.join()

            sites.save_to_yaml()

            log.info(_('Google Scrape: Looking for stragglers.'))
            sites = [s for s in sites if not s.get('skip', False)]

            for site in sites:
                google.save_articles(site, driver)

            log.info(_('Google Scrape: Queue complete!'))
            config.CONFIG['GOOGLE_SCRAPE_ENABLE'] = False
            sites.save_sites_to_yaml()
            config.save_config_to_yaml()


if __name__ == '__main__':
    main()
