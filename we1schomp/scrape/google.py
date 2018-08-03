# -*- coding:utf-8 -*-
""" Scraping tools for the WordPress API.
"""

from gettext import gettext as _
from logging import getLogger
from uuid import uuid4

import selenium

from we1schomp import browser
from we1schomp import clean
from we1schomp import data
from we1schomp.config import config


def save_search_results(site, webdriver):
    """
    """

    log = getLogger(__name__)
    articles = []

    if not config['GOOGLE_SEARCH_ENABLE']:
        log.warning(_('Google Search has been disabled.'))
        return []
    if site.get('skip', False):
        log.warning(_('Skipping: %s'), site['name'])
        return []
    if not site.get('googleSearchEnable', config['GOOGLE_SEARCH_ENABLE']):
        log.warning(_('Google Search disabled: %s'), site['name'])
        return []

    # Perform a Google Search.    
    for query in site.get('queries', config['QUERIES']):
        log.info(_('Searching Google for "%s" at: %s'), query, site['site'])

        # Start the query.
        google_url = config['GOOGLE_QUERY_URL'].format(site=site['site'], query=query)

        # Loop over the page looking for results, then loop over the results.
        while True:

            browser.sleep()
            soup = browser.get_soup_from_selenium(google_url, webdriver)

            # Check for a CAPTCHA. If we find one, hand over execution until
            # it's gone.
            browser.captcha_check(webdriver.current_url)

            for article in yield_articles_on_page(soup, site, query):
                articles.append(article)
                data.save_article_to_json(article)
        
            next_link = soup.find('a', {'id': 'pnnext'})
            if next_link is not None:
                log.info(_('Going to next page.'))
                browser.sleep()
                google_url = f"google.com{next_link.get('href')}"
                continue

            log.info(_('End of results for "%s" at: %s'), query, site['site'])
            break
        
            

    log.info(_('Google search complete for site: %s'), site['name'])
    log.debug(_('Disabling Google Search for site: %s'), site['name'])
    site.update({'googleSearchEnable': False})

    return articles


def yield_articles_on_page(page_soup, site, query):
    """
    """

    log = getLogger(__name__)

    for div in page_soup.find_all('div', {'class': 'rc'}):

        # The link will be the first anchor in the rc div.
        link = div.find('a')
        url = str(link.get('href')).lower()
        log.debug(_('Found Google result: %s'), url)

        if url_has_stopword(url, site):
            continue

        # Sometimes the link's URL gets mushed in with the text. It also
        # should be cleaned of HTML symbols (&lt;, etc.).
        title = clean.from_html(str(link.text).split('http')[0])

        # Parse date from result. This is much more consistant than
        # doing it from the articles themselves, but it can be a little
        # spotty. TODO: Refactor this to catch relative dates.
        try:
            date = div.find('span', {'class': 'f'}).text
            date = str(date).replace(' - ', '')
            log.info(_('Ok: %s'), url)
        except AttributeError:
            date = 'N.D.'
            log.warning(_('Ok (no date): %s'), url)

        # For Google results we'll have to gin up our own slug.
        slug = config['DB_NAME_FORMAT'].format(
            site=site['slug'],
            query=clean.slugify(query),
            slug=clean.slugify(title))   

        yield dict(
            doc_id=str(uuid4()),
            attachment_id='',
            namespace=config['DB_NAMESPACE'],
            name=slug,
            DB_METAPATH=config['DB_METAPATH'].format(site=site['slug']),
            pub=site['name'],
            pub_short=site['slug'],
            title=title,
            url=url,
            content='',  # We don't have content yet--we'll get that next.
            search_term=query)


def save_articles(site, webdriver=None):
    """
    """

    log = getLogger(__name__)

    # Get all the articles associated with this site.
    articles = []
    for article in data.load_articles_from_json():
        if article['pub_short'] == site['slug']:
            articles.append(article)
    if articles == []:
        log.warning(_('No URLs found for site: %s'), site['name'])
        log.info(_('Have you run a Google Search yet?'))
        return []

    log.info(_('Scraping %d articles from site: %s'), len(articles), site['name'])
    for article in articles:

        # Don't waste time on this site if we've updated the stopwords.
        if url_has_stopword(article['url'], site):
            continue

        browser.sleep()
        if not webdriver:
            soup = browser.get_soup_from_url(article['url'])
            if not soup:
                log.warning(_('Could not scrape site with URLLib: %s'), site['name'])
                continue
        else:
            soup = browser.get_soup_from_selenium(article['url'], webdriver)

        # Start by getting rid of JavaScript--Bleach will "neuter" this but
        # has trouble removing it completely.
        try:
            soup.script.extract()
        except AttributeError:
            log.debug(_('No <script> tags found.'))
        
        # Now focus in on the content. We can't guarantee they've used the
        # <article> tag, but it's a safe bet they won't put an article in the
        # <header> or <footer>.
        try:
            soup.header.extract()
            soup.footer.extract()
        except AttributeError:
            log.debug(_('No <header>/<footer> tags found.'))
        
        # Finally, take all the content tags, default <p>, and mush together
        # any that are over a certain length of characters. This can be very
        # imprecise, but it seems to work for the most part. If we're getting
        # particularly bad content for a site, we can tweak the config and
        # try again or switch to a more advanced web-scraping tool.
        tag = site.get('googleContentTag', config['GOOGLE_CONTENT_TAG'])
        length = site.get('googleContentLengthMin', config['GOOGLE_CONTENT_LENGTH_MIN'])
        content = ''
        for div in soup.find_all(tag):
            if len(div.text) > length:
                content += f' {div.text}'
        content = clean.from_html(content)

        article['content'] = content
        data.save_article_to_json(article)
        
    log.info(_('Google scrape complete for site: %s'), site['name'])
    log.debug(_('Setting site to "skip": %s'), site['name'])
    site.update({'skip': True})

    return articles


def url_has_stopword(url, site):
    """ Return "True" if the url has a site's stopword.
    """

    log = getLogger(__name__)

    stopwords = site.get('googleURLStopwords', config['GOOGLE_URL_STOPWORDS'])
    for stop in stopwords:
        if stop in url:
            log.warning(_('Skipping (has "%s"): %s'), stop, url)
            return True
    
    return False
