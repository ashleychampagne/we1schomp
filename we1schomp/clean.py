# -*- coding: utf-8 -*-
""" Functions to clean string data for later processing.
"""

import html
import string
from gettext import gettext as _
from logging import getLogger

import bleach
import regex as re
from unidecode import unidecode

from we1schomp import config


def from_html(dirty):
    """ Removes problematic characters from a string.
    """

    CONFIG = config.SETTINGS

    # Start by Bleaching out the HTML.
    dirty = bleach.clean(dirty, tags=[], strip=True)

    # Get rid of leftovers (&lt;, etc.).
    dirty = html.unescape(dirty)

    # Ideally we shouldn't need this since all the content is being handled
    # "safely," but the LexisNexis import script does it, so we'll do it too
    # in case some other part of the process is expecting ASCII-only text.
    dirty = unidecode(dirty)

    # Regex processing. Experimental!
    if CONFIG['REGEX_ENABLE']:
        dirty = re.sub(re.compile(CONFIG['REGEX_STRING']), ' ', dirty)

    # Squeeze out the whitespace.
    dirty = ''.join(c for c in dirty if c in string.printable)
    dirty = ' '.join(dirty.split())
    clean = dirty.replace(' .', '.')

    return clean


def from_soup(soup, site):
    """
    """

    log = getLogger(__name__)
    CONFIG = config.SETTINGS

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
    tag = site.get('googleContentTag', CONFIG['GOOGLE_CONTENT_TAG'])
    length = site.get('googleContentLengthMin', CONFIG['GOOGLE_CONTENT_LENGTH_MIN'])
    content = ''
    for div in soup.find_all(tag):
        if len(div.text) > length:
            content += f' {div.text}'
    content = from_html(content)
    return content


def slugify(dirty):
    """ Replaces whitespace and punctuation.
    """

    # Titles often have weird punctuation characters in them.
    dirty = html.unescape(dirty)

    # Slugs should be ASCII-only for filename compatibility.
    dirty = unidecode(dirty)

    # Get rid of anything that doesn't belong in a filename.
    dirty = re.sub(re.compile(r'[^a-zA-Z0-9]'), ' ', dirty)

    # Get rid of whitespace.
    dirty = ''.join(c for c in dirty if c in string.printable)
    dirty = '-'.join(dirty.split())
    clean = dirty.strip('-').lower()

    return clean
