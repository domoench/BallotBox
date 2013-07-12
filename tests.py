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

# Mock out some data input. Assume its parsed correctly from the form
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

# Connect to Redis
db = model.Model( HOST, PORT )

def runTests():
  testRedis()
  testCreatePoll()
  testCreateInitiator()
  clearRedis()
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

# TODO: Form Parsing Tests

def testCreatePoll():
  new_poll_key = db.createPoll( poll_data_raw )
  poll_data = json.loads( db.client.get(new_poll_key) )
  check( poll_data['name'] == name )
  check( poll_data['choices'] == choices )
  check( poll_data['close'] == close )
  # TODO: check( poll_data['participants'] == participants )
  check( poll_data['type'] == poll_type )
  # TODO: check( poll_data['initiator'] == initiator )
  clearRedis()

def testCreateInitiator():
  now_str = datetime.datetime.utcnow().isoformat()
  poll_key = helpers.generateKeyString( poll_data_raw['name'], now_str, 'poll_' )
  init_key = helpers.generateKeyString( poll_data_raw['initiator'], now_str, 'init_' )
  init_data_raw = {
    'email': poll_data_raw[ 'initiator' ],
    'poll': poll_key
  }

  # Insert then Check
  db.createInitiator( init_key, init_data_raw )
  init_data = json.loads( db.client.get(init_key) )
  print init_data
  check( init_data_raw['email'] == poll_data_raw['initiator'] )
  check( init_data_raw['poll'] == poll_key )
  clearRedis()

# def testCreateParticipant():

def clearRedis():
  db = model.Model( HOST, PORT )
  for key in db.client.keys( '*' ):
    db.client.delete( key )
  check( len(db.client.keys('*')) == 0 )

if __name__ == '__main__':
  runTests()
