import logging

logging.basicConfig(level=logging.DEBUG)

from we1schomp import config
from we1schomp import data

config, sites = config.load_from_yaml('settings.yaml', 'sites.yaml')

from we1schomp.scrape import wordpress

for site in sites:
    wordpress.check_for_api(site, config)
    for article in wordpress.yield_articles(site, config):
        data.save_article_to_json(article,config, True)

