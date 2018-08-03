# -*- coding: utf-8 -*-
""" Data management functions.
"""

import json
import os
import sys
import time
from gettext import gettext as _
from logging import getLogger

from we1schomp import config, clean


def find_json_files_in_path(path):
    """ Look for all files ending with a json extension.

    This is a generator function and must be funnelled into a list or called as
    part of a loop.

    Args:
        path (str): A folder containing JSON files.

    Yields:
        (dict, str): A dict containing JSON data and its qualified filename.

    TODO:
        If this function were set loose in a production directory with hundreds
        of thousands of files, it would likely be a bit of a nightmare. An
        ideal version would cache this data separately somewhere so that it
        could be called up quickly when necessary without bothering the OS.

        Alternatively, the production server could keep track of everything in
        a separate database, including which files still needed to be scraped.
    """

    for filename in [f for f in os.listdir(path) if f.endswith('.json')]:
        filename = os.path.join(path, filename)
        with open(filename, 'r', encoding='utf-8') as json_file:
            json_data = json.load(json_file)
        yield json_data, filename


def load_articles_from_json(skip_complete_files=True):
    """ Load articles stored as JSON files into memory as dicts.

    Args:
        skip_complete_files (bool): By default, this function will skip
        articles that already have content. Override this by setting to False.

    Returns:
        (list of dict): Article data.
    """

    log = getLogger(__name__)
    path = config.CONFIG['FILE_OUTPUT_PATH']
    articles = []
    count = 0
    skipped = 0

    log.debug(_('Searching for articles: %s'), path)
    for json_data, filename in find_json_files_in_path(path):

        # If a file already has content in it, that implies it's already been
        # scraped. Skip it unless we're told not to.
        if skip_complete_files and json_data['content'] != '':
            log.info(_('Skipping: %s'), filename)
            skipped += 1
            continue

        log.info(_('Ok: %s'), filename)
        count += 1
        articles.append(json_data)

    log.info(_('Found %d files, %d skipped.'), count, skipped)
    return articles


def save_article_to_json(article, allow_overwrite=False):
    """ Save an article to JSON according to the WE1Sv2.0 schema.

    Args:
        article (dict): Article data to save to JSON.
        allow_overwrite (bool): Set to True to update old files. Since this
            requires rooting around in the path, it might come with a big
            performance cost in a production directory.

    Returns:
        bool: True for success.
    """

    log = getLogger(__name__)
    path = config.CONFIG['FILE_OUTPUT_PATH']
    filename = ''

    # Update existing files first.
    if allow_overwrite:
        for json_data, json_file in find_json_files_in_path(path):
            if json_data['doc_id'] == article['doc_id']:
                filename = json_file
                log.info(_('Saving (overwrite): %s'), filename)
                break

    # Otherwise make a new file.
    if not allow_overwrite or filename == '':

        filename = config.CONFIG['FILENAME_FORMAT']

        now = time.localtime()
        timestamp = f'{now.tm_year}{now.tm_mon:02d}{now.tm_mday:02d}'

        # We want to store the search query in the filename if possible. There
        # might be a better way to do this, especially if we eventually want
        # to think about complex boolean search strings.
        query = clean.slugify(article['search_term'])

        filename = filename.format(
            index='{index}',
            timestamp=timestamp,
            site=article['pub_short'],
            query=query
        )

        # Increment filename index so we don't end up overwriting the last
        # thing we saved.
        for index in range(sys.maxsize):
            temp_filename = os.path.join(path, filename.format(index=index))
            if not os.path.exists(temp_filename):
                filename = temp_filename
                break

        log.info(_('Saving: %s'), filename)

    with open(filename, 'w', encoding='utf-8') as json_file:
        json.dump(article, json_file, ensure_ascii=False, indent=2)

    return True
