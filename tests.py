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
db = model.Model(config.conf['HOST'], config.conf['PORT'])

# Mock out some data input. Assume its parsed correctly from the form
name = 'Favorite Color'
choices = ['Red', 'Blue', 'Green', 'Teal']
close = datetime.datetime(2015, 7, 11, 4, 0).isoformat()
participants = ['alouie@gmail.com', 'lluna@gmail.com']
poll_type = 'plurality'
initiator = 'david.moench@arc90.com'
poll_data_raw = {
  'name': name,
  'choices': choices,
  'close': close,
  'participants': participants,
  'type': poll_type,
  'initiator': initiator
}

def runTests():
  testRedis()
  testCreateAndGetPoll()
  testCreateAndGetInitiator()
  testCreateAndGetParticipant()
  clearRedis()
  print 'All tests passed!'

def check(predicate):
  if not predicate:
    raise Exception('Check failed')

def testRedis():
  client = redis.StrictRedis(host=config.conf['HOST'],
                             port=config.conf['PORT'], db=0)
  client.set('v1', 'test value 1')
  check(client.get('v1') == 'test value 1')
  client.delete('v1')
  check(client.get('v1') == None)

# TODO: Form Parsing Tests

def testCreateAndGetInitiator():
  now_str = datetime.datetime.utcnow().isoformat()
  poll_key = helpers.generateKeyString(poll_data_raw['name'], now_str, 'poll_')
  init_key = helpers.generateKeyString(poll_data_raw['initiator'], now_str, 'init_')
  init_data_raw = {
    'email': poll_data_raw['initiator'],
    'poll': poll_key
  }
  # Insert then Check
  db.setInitiator(init_key, init_data_raw)
  init_data = db.getInitiator(init_key)
  check(init_data['email'] == poll_data_raw['initiator'])
  check(init_data['poll'] == poll_key)
  clearRedis()

def testCreateAndGetParticipant():
  now_str = datetime.datetime.utcnow().isoformat()
  poll_key = helpers.generateKeyString(poll_data_raw['name'], now_str, 'poll_')
  part_key = helpers.generateKeyString(poll_data_raw['participants'][0], now_str, 'part_')
  part_data_raw = {
    'email': poll_data_raw['participants'][0],
    'poll': poll_key,
    'voted': True,
    'choice': 1
  }
  # Insert then Check
  db.setParticipant(part_key, part_data_raw)
  part_data = db.getParticipant(part_key)
  check(part_data['email'] == poll_data_raw['participants'][0])
  check(part_data['poll'] == poll_key)
  check(part_data['voted'] == True)
  check(part_data['choice'] == 1)
  clearRedis()

def testCreateAndGetPoll():
  poll_key = db.createPoll(poll_data_raw)
  poll_data = db.getPoll(poll_key)
  check(poll_data['name'] == name)
  check(poll_data['choices'] == choices)
  check(poll_data['close'] == close)
  check(poll_data['type'] == poll_type)
  # Look up initiator info from poll
  init_key = poll_data['initiator']
  init_data = db.getInitiator(init_key)
  check(init_data['email'] == poll_data_raw['initiator'])
  check(init_data['poll'] == poll_key)

  # Look up participants info from poll
  num_participants = len(poll_data_raw['participants'])
  key_count = 0
  for part_key in poll_data['participants']:
    key_count += 1
    part_data = db.getParticipant(part_key)
    check(part_data['poll'] == poll_key)
    check(part_data['email'] in poll_data_raw['participants'])
  check(num_participants == key_count)
  # Look up poll from initiator
  check(poll_data == db.getPoll(init_data['poll']))
  # Look up poll from participant
  check(poll_data == db.getPoll(part_data['poll']))
  clearRedis()

def clearRedis():
  for key in db.client.keys('*'):
    db.client.delete(key)
  check(len(db.client.keys('*')) == 0)

if __name__ == '__main__':
  runTests()
