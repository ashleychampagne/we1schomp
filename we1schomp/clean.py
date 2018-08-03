# -*- coding: utf-8 -*-
""" Functions to clean string data for later processing.
"""

import html
import string

import bleach
import regex as re
from unidecode import unidecode

from we1schomp.config import config


def from_html(dirty):
    """ Process data that probably contained HTML.

    TODO:
        * Regex string needs further testing.
    """

    # Start by Bleaching out the HTML.
    dirty = bleach.clean(dirty, tags=[], strip=True)
    
    # Get rid of leftovers (&lt;, etc.).
    dirty = html.unescape(dirty)

    # Ideally we shouldn't need this since all the content is being handled
    # "safely," but the LexisNexis import script does it, so we'll do it too
    # in case some other part of the process is expecting ASCII-only text.
    dirty = unidecode(dirty)

    # Regex processing. Experimental!
    if config['REGEX_ENABLE']:
        dirty = re.sub(re.compile(config['REGEX_STRING']), ' ', dirty)
    
    # Squeeze out the whitespace.
    dirty = ''.join(c for c in dirty if c in string.printable)
    dirty = ' '.join(dirty.split())
    clean = dirty.replace(' .', '.')

    return clean


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
