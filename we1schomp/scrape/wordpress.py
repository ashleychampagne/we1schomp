# -*- coding:utf-8 -*-
""" Scraping tools for the WordPress API.
"""

import json
import random
from gettext import gettext as _
from logging import getLogger
from uuid import uuid4

from we1schomp import browser
from we1schomp import clean
from we1schomp import data


def check_for_api(site, config):
    """ Check for a WordPress API.

    Returns:
        boolean: True if API present, False if disabled or not found.
    """

    log = getLogger(__name__)
    print()

    # Assume we've already checked for config['ENABLE_WORDPRESS'].
    if not site['wpEnable']:
        log.warning(_('WordPress disabled for site: %s'), site['name'])
        return False

    log.info(_('Testing WordPress API for site: %s'), site['name'])
    wp_url = f"http://{site['url'].strip('/')}{config['WORDPRESS_API_URL']}"
    browser.sleep(config)
    response = browser.get_json_from_url(wp_url)

    if not response:
        log.warning(_('No API or bad response.'))
        return False
    if response['namespace'] != 'wp/v2':
        log.warning(_('Wrong API version or bad response.'))
        return False

    log.info(_('Ok!'))
    return True


def yield_articles(site, config):
    """ Look for articles at a site using the WordPress API.
    
    This is a generator function and must be funnelled into a list or called as
    part of a loop.

    Args:
        site (dict): A dict of settings for a particular site.
        config (dict): A dict of global settings for scraping.

    Yields:
        dict: An article ready for JSON processing.

    Returns:
        list: Will return a null list if no results found.
    """

    log = getLogger(__name__)
    print()

    # Perform the API query.
    log.info(_('Starting WordPress scrape for site: %s'), site['name'])
    results = []
    wp_url = f"http://{site['url'].strip('/')}{config['WORDPRESS_API_URL']}"

    for query in site['queries']:
        query_results = []

        if not (config['WORDPRESS_GET_PAGES'] and site['wpPagesEnable']):
            log.warning(_('Skipping pages (disabled).'))
        else:
            wp_query = config['WORDPRESS_PAGES_QUERY_URL'].format(
                api_url=wp_url, query=query.replace(' ', '+'))
            log.info(_('Querying pages: %s'), wp_query)
            browser.sleep()
            query_results += browser.get_json_from_url(wp_query)

        if not (config['WORDPRESS_GET_POSTS'] and site['wpPostsEnable']):
            log.warning(_('Skipping posts (disabled).'))
        else:
            wp_query = config['WORDPRESS_POSTS_QUERY_URL'].format(
                api_url=wp_url, query=query.replace(' ', '+'))
            log.info(_('Querying posts: %s'), wp_query)
            browser.sleep()
            query_results += browser.get_json_from_url(wp_query)
        
        # Collate results with query terms.
        for query_result in query_results:
            results.append((query, query_result))

    # If we're not finding anything, it's time to give up.
    if results == []:
        log.info(_('No WordPress API results for site: %s'), site['name'])
        site.update({'wpEnable': False})
        return []

    # Otherwise, process and yield the results.
    for query, query_result in results:

        # WordPress helpfully provides a slug we can use for our article.
        slug = config['DB_NAME_FORMAT'].format(
            site=site['slug'], query=clean.slugify(query), slug=query_result['slug'])

        article = dict(
            doc_id=str(uuid4()),
            attachment_id='',
            namespace=config['NAMESPACE'],
            name=slug,
            metapath=config['METAPATH'].format(site=site['slug']),
            pub=site['name'],
            pub_short=site['slug'],
            title=clean.from_html(query_result['title']['rendered'], config),
            url=query_result['link'],
            content=clean.from_html(query_result['content']['rendered'], config),
            search_term=query
        )

        yield article

    log.info(_('Scrape complete: %s'), site['name'])
    site.update({'skip': True})
