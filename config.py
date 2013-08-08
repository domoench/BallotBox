"""
BallotBox configuration values

"""
from json import loads

# Get config values from config.json
with open('config.json', 'r') as fp:
    config_str = fp.read()
    config = loads(config_str)

    DOMAIN_ROOT = config['DOMAIN_ROOT']
    LOG_FILE = config['LOG_FILE']
    EMAIL_SOURCE = config['EMAIL_SOURCE']
    MANDRILL_USER = config['MANDRILL_USER']
    MANDRILL_PASS = config['MANDRILL_PASS']
    REDIS_HOST = config['REDIS_HOST']
    REDIS_PORT = config['REDIS_PORT']
    REDISCLOUD_URL = config['REDISCLOUD_URL']

"""
conf = {
    'DOMAIN_ROOT': 'http://localhost:5000',
    'LOG_FILE': 'log.txt',
    'EMAIL_SOURCE': 'david.moench@arc90.com' # Where BB notification emails will come from
}
"""
