"""
BallotBox Test Suite.

Instructions:
  Start the following processes:
    1. redis-server
    2. BallotBox's virtualenv
    3. application.py server
  Then, 'python tests.py'
"""
import redis
import model
import config
import helpers
import datetime
import json

# CONFIG
HOST = config.conf[ 'HOST' ]
PORT = config.conf[ 'PORT' ]

def runTests():
  testRedis()
  testCreatePoll()
  print 'All tests passed!'

def check( predicate ):
  if not predicate:
    raise Exception( 'Check failed' )

def testRedis():
  client = redis.StrictRedis( host = HOST, port = PORT, db = 0 )
  client.set( 'v1', 'test value 1' )
  check( client.get('v1') == 'test value 1' )
  client.delete( 'v1' )
  check( client.get('v1') == None )

def testModel():
  db = model.Model( HOST, PORT )
  # TODO: How to test?

# TODO: Form Parsing Tests

def testCreatePoll():
  db = model.Model( HOST, PORT )

  # Assume its parsed from the form
  name = 'Favorite Color'
  choices = [ 'Red', 'Blue', 'Green', 'Teal' ]
  close = datetime.datetime(2015, 7, 11, 4, 0).isoformat()
  participants = [ 'alouie@gmail.com', 'lluna@gmail.com' ]
  poll_type = 'majority'
  initiator = 'david.moench@arc90.com'
  poll_data_raw = {
    'name': name,
    'choices': choices,
    'close': close,
    'participants': participants,
    'type': poll_type,
    'initiator': initiator
  }

  new_poll_key = db.createPoll( poll_data_raw )
  poll_data = json.loads( db.client.get(new_poll_key) )
  check( poll_data['name'] == name )
  check( poll_data['choices'] == choices )
  check( poll_data['close'] == close )
  # check( poll_data['participants'] == participants )
  check( poll_data['type'] == poll_type )
  # check( poll_data['initiator'] == initiator )

if __name__ == '__main__':
  runTests()
