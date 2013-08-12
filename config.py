"""
BallotBox configuration values
"""
import os

# Get config values from the environment
DOMAIN_ROOT = os.environ['DOMAIN_ROOT']
EMAIL_SOURCE = os.environ['EMAIL_SOURCE']
MANDRILL_USER = os.environ['MANDRILL_USER']
MANDRILL_PASS = os.environ['MANDRILL_PASS']
REDISCLOUD_URL = os.environ['REDISCLOUD_URL']
