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
  MANDRILL_KEY = config['MANDRILL_KEY']
  REDIS_HOST = config['REDIS_HOST']
  REDIS_PORT = config['REDIS_PORT']
