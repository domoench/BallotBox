"""
BallotBox configuration values
"""
import os

# Get config values from the environment
DOMAIN_ROOT = os.environ['DOMAIN_ROOT']
EMAIL_SOURCE = os.environ['EMAIL_SOURCE']
MANDRILL_KEY = os.environ['MANDRILL_KEY']
REDISCLOUD_URL = os.environ['REDISCLOUD_URL']
