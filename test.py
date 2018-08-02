from we1schomp import config

config, sites = config.load_from_yaml('settings.yaml', 'sites.yaml')

from we1schomp.scrape import wordpress

for site in sites:
    wordpress.check_for_api(site, config)