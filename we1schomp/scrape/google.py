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


def url_has_stopword(url, site):
    """ Return "True" if the url has a site's stopword.
    """

    for stop in site['googleURLStopwords']:
        if stop in url:
            return True
    
    return False


def yield_search_results(site, config, webdriver):
    """
    """

    log = getLogger(__name__)
    print()

    # Assume we've already checked for config['GOOGLE_SEARCH_ENABLE'].
    if not site['googleSearchEnable']:
        log.warning(_('Google Search disabled for site: %s'), site['name'])
        return []
    
    for query in site['queries']:
        log.info(_('Searching Google for "%s" at: %s'), query, site['url'])

        # Start the query.
        google_url = config['GOOGLE_QUERY_URL'].format(site=site['url'], query=query)

        # Loop over the page looking for results, then loop over the results.
        while True:

            browser.sleep()
            soup = browser.get_soup_from_url(google_url, config, webdriver, force_selenium=True)

            # Check for a CAPTCHA. If we find one, hand over execution until
            # it's gone.
            browser.captcha_check(webdriver.current_url, config)

            for div in soup.find_all('div', {'class': 'rc'}):

                # The link will be the first anchor in the rc div.
                link = div.find('a')
                url = str(link.get('href')).lower()

                if url_has_stopword(url, site):
                    log.warning(_('Skipping (stopword): %s'), url)
                    continue

                # Sometimes the link's URL gets mushed in with the text. It also
                # should be cleaned of HTML symbols (&lt;, etc.).
                title = clean.from_html(str(link.text).split('http')[0], config)

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
                    slug=clean.slugify(title)
                )   

                article = dict(
                    doc_id=str(uuid4()),
                    attachment_id='',
                    namespace=config['NAMESPACE'],
                    name=slug,
                    metapath=config['METAPATH'].format(site=site['slug']),
                    pub=site['name'],
                    pub_short=site['slug'],
                    title=title,
                    url=link,
                    content='',  # We don't have content yet--we'll get that next.
                    search_term=query
                )

                yield article
        
            try:
                next_link = webdriver.find_element_by_id('pnnext')
            except selenium.common.exceptions.NoSuchAttributeException:
                log.info(_('End of results for "%s" at: %s'), query, site['url'])
                break
        
            log.info(_('Going to next page.'))
            browser.sleep(config)
            google_url = str(next_link.get('href'))

    log.info(_('Google search complete for site: %s'), site['name'])


def get_content(site, config, webdriver):
    """
    """

    log = getLogger(__name__)
    print()

    # Get all the articles associated with this site.
    articles = []
    for article in data.load_articles_from_json(config):
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
            log.warning(_('Skipping (stopword): %s'), article['url'])
            continue

        browser.sleep(config)
        soup = browser.get_soup_from_url(article['url'], config, webdriver)

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
        content = ''
        for tag in soup.find_all(site['googleContentTag']):
            if len(tag.text) > site['googleContentLengthMin']:
                content += f' {tag.text}'
        content = clean.from_html(content, config)
        
        article.update({'content': content})
        yield article

    log.info(_('Google scrape complete for site: %s'), site['name'])
