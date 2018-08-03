# -*- coding:utf-8 -*-
""" Scraping tools for the WordPress API.
"""

from gettext import gettext as _
from logging import getLogger
from uuid import uuid4

from we1schomp import browser, clean, config, data


def check_for_api(site):
    """ Check for a WordPress API.

    Returns:
        bool: True if API present, False if disabled or not found.
    """

    log = getLogger(__name__)
    CONFIG = config.SETTINGS

    if not CONFIG['WORDPRESS_ENABLE'] or site.get('skip', False):
        log.warning(_('Skipping: %s'), site['name'])
        return False
    if not site.get('wpEnable', CONFIG['WORDPRESS_ENABLE']):
        log.warning(_('WordPress disabled: %s'), site['name'])
        return False

    log.info(_('Testing WordPress API for site: %s'), site['name'])
    wp_url = f"http://{site['site'].strip('/')}{CONFIG['WORDPRESS_API_URL']}"

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
    CONFIG = config.SETTINGS

    pages_ok = CONFIG['WORDPRESS_GET_PAGES'] and site.get('wpPagesEnable', True)
    posts_ok = CONFIG['WORDPRESS_GET_POSTS'] and site.get('wpPostsEnable', True)

    for query in site.get('queries', CONFIG['QUERIES']):

        # Query pages, if enabled.
        if not pages_ok:
            log.warning(_('Skipping pages (disabled): %s'), site['name'])
        else:
            wp_query = CONFIG['WORDPRESS_PAGES_QUERY_URL'].format(
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
            wp_query = CONFIG['WORDPRESS_POSTS_QUERY_URL'].format(
                api_url=site['wpURL'],
                query=query.replace(' ', '+'))
            log.info(_('Querying posts: %s'), wp_query)
            browser.sleep()
            for response in browser.get_json_from_url(wp_query):
                yield query, response


def save_articles(site):
    """ Look for articles at a site using the WordPress API.

    Returns:
        list: [] if no results found.
    """

    log = getLogger(__name__)
    CONFIG = config.SETTINGS
    articles = []

    if not check_for_api(site):
        return articles

    # Perform the API query.
    log.info(_('Starting WordPress scrape for site: %s'), site['name'])
    for query, query_result in yield_query_results(site):

        # WordPress helpfully provides a slug we can use for our article.
        slug = CONFIG['DB_NAME_FORMAT'].format(
            site=site['slug'], query=clean.slugify(query), slug=query_result['slug'])

        article = dict(
            doc_id=str(uuid4()),
            attachment_id='',
            namespace=CONFIG['DB_NAMESPACE'],
            name=slug,
            metapath=CONFIG['DB_METAPATH'].format(site=site['slug']),
            pub=site['name'],
            pub_short=site['slug'],
            title=clean.from_html(query_result['title']['rendered']),
            url=query_result['link'],
            content=clean.from_html(query_result['content']['rendered']),
            search_term=query)
        data.save_article_to_json(article)
        articles.append(article)

    # Pass this site on to Google if we're not getting WordPress results.
    if articles == []:
        log.info(_('No WordPress API results for site: %s'), site['name'])
        site['wpEnable'] = False
        return articles

    log.info(_('Scrape complete: %s'), site['name'])
    log.debug(_('Setting site to "skip": %s'), site['name'])
    site['skip'] = True
    return articles
