"""
"""

import logging
from gettext import gettext as _
from multiprocessing.dummy import Pool as ThreadPool

import we1schomp
from we1schomp import browser
from we1schomp.config import CONFIG, SITES
from we1schomp.scrape import google, wordpress

we1schomp.config.load_config_from_yaml()
we1schomp.config.load_sites_from_yaml()

logging.basicConfig(level=logging.INFO)


def main():
    """
    """

    log = logging.getLogger(__name__)
    driver = browser.get_webdriver()

    while True:

        # Get all sites not flagged "skip". If all sites are flagged, we're done!
        sites = [s for s in SITES if not s.get('skip', False)]
        if sites == []:
            log.info(_('Queue finished. Goodbye!'))
            return

        # WordPress
        if CONFIG['WORDPRESS_ENABLE']:
            log.info(_('WordPress: Starting queue.'))

            pool = ThreadPool(CONFIG['THREAD_POOL_SIZE'])
            pool.map(wordpress.save_articles, sites)
            pool.close()
            pool.join()

            log.info(_('WordPress: Queue complete!'))
            CONFIG['WORDPRESS_ENABLE'] = False
            we1schomp.config.save_sites_to_yaml()
            we1schomp.config.save_config_to_yaml()
            continue

        # Google Search
        if CONFIG['GOOGLE_SEARCH_ENABLE']:
            log.info(_('Google Search: Starting queue.'))

            for site in sites:
                google.save_search_results(site, driver)

            log.info(_('Google Search: Queue complete!'))
            CONFIG.update({'GOOGLE_SEARCH_ENABLE': False})
            we1schomp.config.save_sites_to_yaml()
            we1schomp.config.save_config_to_yaml()
            continue

        # Google Scrape
        if CONFIG['GOOGLE_SCRAPE_ENABLE']:
            log.info(_('Google Scrape: Starting queue.'))

            pool = ThreadPool(CONFIG['THREAD_POOL_SIZE'])
            pool.map(google.save_articles, sites)
            pool.close()
            pool.join()

            we1schomp.config.save_sites_to_yaml()

            log.info(_('Google Scrape: Looking for stragglers.'))
            sites = [s for s in sites if not s.get('skip', False)]

            for site in sites:
                google.save_articles(site, driver)

            log.info(_('Google Scrape: Queue complete!'))
            CONFIG.update({'GOOGLE_SCRAPE_ENABLE': False})
            we1schomp.config.save_config_to_yaml()


if __name__ == '__main__':
    main()
