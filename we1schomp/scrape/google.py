# -*- coding:utf-8 -*-
""" Scraping tools for Google.
"""

from gettext import gettext as _
from logging import getLogger
from uuid import uuid4

from we1schomp import browser, clean, data, settings


def is_selenium_site(site):
    """
    """

    log = getLogger(__name__)

    if site['seleniumCollection']:
        log.info(_('URLLib disabled: %s'), site)
        return True

    # Try to get the site's content. If we fail, it may be because the site
    # has generic GET methods blocked and we'll have to use Selenium.
    log.debug(_('Testing URLLib for site: %s'), site['name'])
    soup = browser.get_soup_from_url(site['url'])
    if not soup:
        log.info(_('URLLib disabled: %s'), site['name'])
        site['seleniumCollection'] = True
        return True
    return False


def is_stopword_in_url(url, site):
    """ Return "True" if the url has a site's stopword.
    """

    log = getLogger(__name__)
    config = settings.CONFIG

    stopwords = site.get('googleURLStopwords', config['GOOGLE_URL_STOPWORDS'])
    for stop in stopwords:
        if stop in url:
            log.warning(_('Skipping (has "%s"): %s'), stop, url)
            return True
    return False


def yield_query_results(site, driver):
    """
    """

    log = getLogger(__name__)
    config = settings.CONFIG

    for query in site.get('queries', config['QUERIES']):
        log.info(_('Searching Google for "%s" at: %s'), query, site['name'])

        # Loop over each page looking for results.
        google_url = config['GOOGLE_QUERY_URL'].format(site=site['site'], query=query)
        while True:

            browser.sleep()
            soup = browser.get_soup_from_selenium(google_url, driver)

            # Loop over each "Result Candidate" in the page.
            for div in soup.find_all('div', {'class': 'rc'}):

                # The link will be the first anchor in the div.
                link = div.find('a')
                url = str(link.get('href')).lower()
                log.debug(_('Found Google result: %s'), url)

                # Check for URL stopwords.
                if is_stopword_in_url(url, site):
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
                except AttributeError:
                    date = 'N.D.'
                    log.warning(_('Ok (no date): %s'), url)

                yield dict(url=url, title=title, date=date)

            next_link = soup.find('a', {'id': 'pnnext'})
            if next_link is not None:
                log.info(_('Going to next page.'))
                browser.sleep()
                google_url = f"http://google.com{next_link.get('href')}"
                continue

            log.info(_('End of results for "%s" at: %s'), query, site['site'])
            break

    log.info(_('Google search complete for site: %s'), site['name'])


def scrape_site(site, articles, driver, allow_search=True):
    """
    """

    log = getLogger(__name__)
    config = settings.CONFIG

    # We only need the articles related to this site.
    site_articles = [a for a in articles if a['pub_short'] == site['slug']]

    # Google Search
    if allow_search and not site.get('googleSearchEnable', True):
        log.info(_('Google Search disabled for site: %s'), site['name'])
    if allow_search and site.get('googleSearchEnable', True):

        # If we're searching, don't collect stuff we already have.
        skip_urls = [a['url'] for a in site_articles]

        # Find results.
        log.info(_('Starting Google Search for site: %s'), site['name'])
        for query, query_result in yield_query_results(site, driver):

            if query_result['url'] in skip_urls:
                log.info(_('Skipping (duplicate): %s'), query_result['url'])
                continue

            # For Google results we'll have to gin up our own slug.
            slug = config['DB_NAME_FORMAT'].format(
                site=site['slug'],
                query=clean.slugify(query),
                slug=clean.slugify(query_result['title']))

            if not is_selenium_site(site):
                soup = browser.get_soup_from_url(query_result['url'])
            else:
                soup = browser.get_soup_from_selenium(query_result['url'], driver)
            content = clean.from_soup(soup, site)

            # Create a new article.
            article = dict(
                doc_id=str(uuid4),
                attachment_id='',
                namespace=config['DB_NAMESPACE'],
                name=slug,
                pub_date=query_result['date'],
                metapath=config['DB_METAPATH'].format(site=site['slug']),
                pub=site['name'],
                pub_short=site['slug'],
                title=query_result['title'],
                url=query_result['url'],
                content=content,
                length=f'{len(content)} words',
                search_term=query)

            # Save the results.
            data.save_article_to_json(article)
            articles.append(article)
            skip_urls.append(query_result['url'])

    # Google Scrape
    if not site.get('googleScrapeEnable', True):
        log.info(_('Google Scrape disabled for site: %s'), site['name'])
    if site.get('googleScrapeEnable', True):

        # If there's no articles to scrape, let's drop out here.
        if articles == []:
            log.warning(_('No articles found for site: %s'), site['name'])
            return articles

        log.info(_('Starting Google scrape for site: %s'), site['name'])
        for article in articles:

            if not is_selenium_site(site):
                soup = browser.get_soup_from_url(article['url'])
            else:
                soup = browser.get_soup_from_selenium(article['url'], driver, use_new_tab=True)
            content = clean.from_soup(soup, site)

            # Update old articles -- don't save new ones.
            article.update({'content': content, 'length': f'{len(content)} words'})
            data.save_article_to_json(article, update_files=True)

    log.info(_('Scrape complete: %s'), site['name'])
    site['skip'] = True
    config.save_sites_to_yaml()
    return articles


def scrape(sites, driver):
    """
    """

    log = getLogger(__name__)
    config = settings.CONFIG
    articles = []

    if not config['GOOGLE_SEARCH_ENABLE']:
        log.warning(_('Google Search has been disabled.'))
        return articles

    # Grab what we've done so far.
    articles = data.load_articles_from_json()

    # Look for stragglers that need cleaning up.
    for site in sites:
        articles = scrape_site(site, articles, driver, allow_search=False)

    # Now jump into our search.
    for site in sites:
        articles = scrape_site(site, articles, driver)

    # And scrape what we got!
    for site in sites:
        articles = scrape_site(site, articles, driver, allow_search=False)

    return articles
