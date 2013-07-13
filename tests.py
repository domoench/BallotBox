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
md = model.Model(config.conf['HOST'], config.conf['PORT'])

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
  testAddPollParticipants()
  testVote()
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
  md.setInitiator(init_key, init_data_raw)
  init_data = md.getInitiator(init_key)
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
  md.setParticipant(part_key, part_data_raw)
  part_data = md.getParticipant(part_key)
  check(part_data['email'] == poll_data_raw['participants'][0])
  check(part_data['poll'] == poll_key)
  check(part_data['voted'] == True)
  check(part_data['choice'] == 1)
  clearRedis()

def testCreateAndGetPoll():
  poll_key = md.createPoll(poll_data_raw)
  poll_data = md.getPoll(poll_key)
  check(poll_data['name'] == name)
  check(poll_data['choices'] == choices)
  check(poll_data['close'] == close)
  check(poll_data['type'] == poll_type)
  # Look up initiator info from poll
  init_key = poll_data['initiator']
  init_data = md.getInitiator(init_key)
  check(init_data['email'] == poll_data_raw['initiator'])
  check(init_data['poll'] == poll_key)

  # Look up participants info from poll
  num_participants = len(poll_data_raw['participants'])
  key_count = 0
  for part_key in poll_data['participants']:
    key_count += 1
    part_data = md.getParticipant(part_key)
    check(part_data['poll'] == poll_key)
    check(part_data['email'] in poll_data_raw['participants'])
  check(num_participants == key_count)
  # Look up poll from initiator
  check(poll_data == md.getPoll(init_data['poll']))
  # Look up poll from participant
  check(poll_data == md.getPoll(part_data['poll']))
  clearRedis()

def testVote():
  poll_key = md.createPoll(poll_data_raw)
  poll_data = md.getPoll(poll_key)
  for part_key in poll_data['participants']:
    md.vote(part_key, 0)
    participant = md.getParticipant(part_key)
    choice = participant['choice']
    check(choice == 0)
    check(poll_data['choices'][choice] == poll_data_raw['choices'][choice])
  clearRedis()

def testAddPollParticipants():
  poll_key = md.createPoll(poll_data_raw)
  # Insert
  new_participants = []
  for i in range(0, 300):
    new_participants.append(str(i) + '@gmail.com')
  md.addPollParticipants(poll_key, new_participants)
  # Check
  poll_participants = md.getPoll(poll_key)['participants']
  for part_key in poll_participants.keys():
    part_data = md.getParticipant(part_key)
    check(part_data['choice'] == None)
    check(part_data['poll'] == poll_key)
    check(part_data['voted'] == False)
    check(part_data['email'] == poll_participants[part_key])
  clearRedis()

def clearRedis():
  for key in md.client.keys('*'):
    md.client.delete(key)
  check(len(md.client.keys('*')) == 0)

if __name__ == '__main__':
  runTests()
