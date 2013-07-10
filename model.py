"""
  Handles interaction between BallotBox Flask app and Redis DB
"""
import redis
import hashlib
import json
import datetime

class Model:
  def __init__( self, host, port ):
    self.host = host
    self.port = port
    self.client = redis.StrictRedis( host = self.host, port = self.port, db = 0 )

  def createPoll( self, poll_data ):
    """
    Create a new poll record on the DB

    poll_data is a python dictionary. Its structure is described here:
    https://gist.github.com/domoench/36c9a3bddbf2f8676a07
    """

    self.client.set( 'test_key', poll_data )
