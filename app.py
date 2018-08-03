import logging
from gettext import gettext as _
from multiprocessing.dummy import Pool as ThreadPool

from we1schomp import browser, config, data
from we1schomp.scrape import google, wordpress

config.load_from_yaml('settings.yaml', 'sites.yaml')

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

driver = browser.get_webdriver()


def main():
    """
    """

    while True:

        # Get all sites not flagged "skip". If all sites are flagged, we're done!
        sites = [s for s in config.sites if not s.get('skip', False)]
        if sites == []:
            log.info(_('Queue finished. Goodbye!'))
            return

        # WordPress
        if config.config['WORDPRESS_ENABLE']:
            log.info(_('WordPress: Starting queue.'))

            pool = ThreadPool(config.config['THREAD_POOL_SIZE'])
            pool.map(wordpress.save_articles, sites)
            pool.close()
            pool.join()

            log.info(_('WordPress: Queue complete!'))
            config.config['WORDPRESS_ENABLE'] = False
            config.save_to_yaml()
            continue

        # Google Search
        if config.config['GOOGLE_SEARCH_ENABLE']:
            log.info(_('Google Search: Starting queue.'))

            for site in sites:
                google.save_search_results(site, driver)

            log.info(_('Google Search: Queue complete!'))
            config.config.update({'GOOGLE_SEARCH_ENABLE': False})
            config.save_to_yaml()
            continue

        # Google Scrape
        if config.config['GOOGLE_SCRAPE_ENABLE']:
            log.info(_('Google Scrape: Starting queue.'))

            pool = ThreadPool(config.config['THREAD_POOL_SIZE'])
            pool.map(google.save_articles, sites)
            pool.close()
            pool.join()

            config.save_to_yaml()

            log.info(_('Google Scrape: Looking for stragglers.'))
            sites = [s for s in sites if not s.get('skip', False)]

            for site in sites:
                google.save_articles(site, driver)
            
            log.info(_('Google Scrape: Queue complete!'))
            config.config.update({'GOOGLE_SCRAPE_ENABLE': False})
            config.save_to_yaml()


if __name__ == '__main__':
    main()
