# -*- coding:utf-8 -*-
""" Scraping tools for the WordPress API.
"""

from functools import partial
from gettext import gettext as _
from logging import getLogger
from multiprocessing.dummy import Lock
from multiprocessing.dummy import Pool as ThreadPool
from uuid import uuid4

from we1schomp import browser, clean, data, settings


def is_wordpress_site(site):
    """ Check for a WordPress API.

    Returns:
        bool: True if API present, False if disabled or not found.
    """

    log = getLogger(__name__)
    config = settings.CONFIG

    if not (site.get('wpEnable', True) and config['WORDPRESS_ENABLE']):
        log.warning(_('Skipping site (disabled): %s'), site['name'])
        return False

    log.debug(_('Testing WordPress API for site: %s'), site['name'])
    wp_url = f"http://{site['site'].strip('/')}{config['WORDPRESS_API_URL']}"

    # Do we already have a WordPress API URL?
    if site.get('wpURL') == wp_url:
        return True

    # If not, try and dig one up.
    browser.sleep()
    response = browser.get_json_from_url(wp_url)

    if not response:
        log.warning(_('No API or bad response: %s'), site['name'])
        return False
    if response['namespace'] != 'wp/v2':
        log.warning(_('Wrong API version or bad response: %s'), site['name'])
        return False

    # Store it so we don't have to do this query again.
    site['wpURL'] = wp_url
    return True


def yield_query_results(site):
    """ Find posts and pages at a WordPress site.

    Yields:
        (str, dict): An article ready for JSON processing and the query that
        was used to find it.
    """

    log = getLogger(__name__)
    config = settings.CONFIG

    pages_ok = config['WORDPRESS_GET_PAGES'] and site.get('wpPagesEnable', True)
    posts_ok = config['WORDPRESS_GET_POSTS'] and site.get('wpPostsEnable', True)

    for query in site.get('queries', config['QUERIES']):

        if not is_wordpress_site(site):
            continue

        # Query pages, if enabled.
        if not pages_ok:
            log.warning(_('Skipping pages (disabled): %s'), site['name'])
        else:
            wp_query = config['WORDPRESS_PAGES_QUERY_URL'].format(
                api_url=site['wpURL'],
                query=query.replace(' ', '+'))
            log.info(_('Querying pages: %s'), wp_query)
            browser.sleep()
            for response in browser.get_json_from_url(wp_query):
                yield query, response

        # Query posts, if enabled.
        if not posts_ok:
            log.warning(_('Skipping posts (disabled): %s'), site['name'])
        else:
            wp_query = config['WORDPRESS_POSTS_QUERY_URL'].format(
                api_url=site['wpURL'],
                query=query.replace(' ', '+'))
            log.info(_('Querying posts: %s'), wp_query)
            browser.sleep()
            for response in browser.get_json_from_url(wp_query):
                yield query, response


def scrape_site(site, collected_urls, lock):
    """ Scrape all articles for all terms from a specified site.
    """

    log = getLogger(__name__)
    config = settings.CONFIG
    articles = []

    if not is_wordpress_site(site):
        return articles

    # Perform the API query.
    log.info(_('Starting WordPress scrape for site: %s'), site['name'])
    for query, query_result in yield_query_results(site):

        # Don't collect stuff we already have.
        if query_result['link'] in collected_urls:
            log.info(_('Skipping (duplicate): %s'), query_result['url'])
            continue

        # WordPress helpfully provides a slug we can use for our article.
        slug = config['DB_NAME_FORMAT'].format(
            site=site['slug'], query=clean.slugify(query), slug=query_result['slug'])

        article = dict(
            doc_id=str(uuid4()),
            attachment_id='',
            namespace=config['DB_NAMESPACE'],
            name=slug,
            pub_date=query_result['date'],
            metapath=config['DB_METAPATH'].format(site=site['slug']),
            pub=site['name'],
            pub_short=site['slug'],
            title=clean.from_html(query_result['title']['rendered']),
            url=query_result['link'],
            content=clean.from_html(query_result['content']['rendered']),
            search_term=query)

        if lock is not None:
            lock.acquire()
        data.save_article_to_json(article)
        articles.append(article)
        collected_urls.append(query_result['link'])
        if lock is not None:
            lock.release()

    log.info(_('Scrape complete: %s'), site['name'])
    if articles == []:
        log.info(_('No WordPress API results for site: %s'), site['name'])
        site['wpEnable'] = False
    else:
        log.debug(_('Setting site to "skip": %s'), site['name'])
        site['skip'] = True

    if lock is not None:
        lock.acquire()
    settings.save_to_yaml()
    if lock is not None:
        lock.release()

    return articles


def scrape(sites):
    """ Look for articles at a site using the WordPress API.
    """

    log = getLogger(__name__)
    config = settings.CONFIG
    articles = []

    if not config['WORDPRESS_ENABLE']:
        log.warning(_('WordPress has been disabled.'))
        return articles

    # Don't re-collect the same URLs.
    collected_urls = [a['url'] for a in data.load_articles_from_json()]

    # Open a new thread pool.
    thread_pool = ThreadPool(config['THREAD_POOL_SIZE'])
    lock = Lock()

    # Queue up collection.
    collection_task = partial(scrape_site, collected_urls=collected_urls, lock=lock)
    articles = thread_pool.map(collection_task, sites)

    # Get the pool running.
    thread_pool.close()
    thread_pool.join()

    return articles
