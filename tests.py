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
import random
import math
import smtplib
from email.mime.text import MIMEText

# CONFIG
md = model.Model(config.conf['HOST'], config.conf['PORT'])

# Mock out some data input. Assume its parsed correctly from the form
name = 'Favorite Color'
choices = ['Red', 'Blue', 'Green', 'Teal']
close = datetime.datetime(2015, 7, 11, 4, 0).isoformat()
print close
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
  testCheckPollOngoing()
  testCalcStats()
  testGetAllVotes()
  testGetParticipantVoteLinks()
  testDeletePerson()
  # testSmtp()
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
    check(participant['voted'] == True)
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

def testCheckPollOngoing():
  # Ongoing
  poll1_key = md.createPoll(poll_data_raw)
  check(md.checkPollOngoing(poll1_key))
  poll1_data = md.getPoll(poll1_key)
  check(poll1_data['ongoing'] == True)

  # Ongoing, but all participants have voted
  poll2_key = md.createPoll(poll_data_raw)
  poll2_data = md.getPoll(poll2_key)
  poll2_part_keys = poll2_data['participants'].keys()
  for part_key in poll2_part_keys:
    md.vote(part_key, 0)
  check(not md.checkPollOngoing(poll2_key))
  poll2_data = md.getPoll(poll2_key)
  check(poll2_data['ongoing'] == False)

  # Ongoing, but time is up
  poll3_key = md.createPoll(poll_data_raw)
  poll3_data = md.getPoll(poll3_key)
  poll3_data['close'] = datetime.datetime(1987, 5, 20, 4, 0).isoformat()
  md.client.set(poll3_key, json.dumps(poll3_data))
  check(not md.checkPollOngoing(poll3_key))
  poll3_data = md.getPoll(poll3_key)
  check(poll3_data['ongoing'] == False)

  clearRedis()

def testCalcStats():
  results = helpers.calcStats([0, 3, 2, 1, 1, 0, 1, 0, 1, 3], 4)
  expected = {0: 30, 1: 40, 2: 10, 3: 20}
  check(results == expected)

# This basically simulates the lifecycle of an entire vote
def testGetAllVotes():
  poll_key = md.createPoll(poll_data_raw)
  # Insert
  new_participants = []
  for i in range(0, 100):
    new_participants.append(str(i) + '@gmail.com')
  md.addPollParticipants(poll_key, new_participants)
  # Vote
  participants = md.getPoll(poll_key)['participants']
  for part_key in participants:
    md.vote(part_key, random.randint(0, 3))
  md.closePoll(poll_key)
  poll_data = md.getPoll(poll_key)
  check(len(poll_data['participants']) == 102)
  choices_list = md.getAllVotes(poll_key)
  results = helpers.calcStats(choices_list, 4)
  total_percent = 0
  for key in results:
    total_percent += results[key]
  check(math.fabs(total_percent - 100.0) < 0.00001)
  clearRedis()

def testDeletePerson():
  poll_key = md.createPoll(poll_data_raw)
  participants = md.getPoll(poll_key)['participants']
  for part_key in participants:
    md.deletePerson(part_key)
  md.deletePerson(md.getPoll(poll_key)['initiator'])
  # Only the poll record remains
  check(len(md.client.keys('*')) == 1)
  clearRedis()

def testSmtp():
  from_addr = 'david.moench@arc90.com'
  to_addr = 'david.moench@arc90.com'
  msg = MIMEText('Flask generated this email. Yay')
  msg['Subject'] = 'BallotBox Test Email'
  msg['From'] = from_addr
  msg['To'] = to_addr
  # Fire up our SMTP server
  print msg.as_string()
  s = smtplib.SMTP('localhost')
  s.sendmail(from_addr, [to_addr], msg.as_string())
  s.quit()

def testGetParticipantVoteLinks():
  poll_key = md.createPoll(poll_data_raw)
  # Insert
  new_participants = []
  for i in range(0, 100):
    new_participants.append(str(i) + '@gmail.com')
  md.addPollParticipants(poll_key, new_participants)
  poll_data = md.getPoll(poll_key)
  results = md.getParticipantVoteLinks(poll_key)
  for pair in results:
    vote_link = pair['vote_link']
    check(vote_link[71:] in poll_data['participants'])
    check(vote_link[1:70] == poll_key)

  clearRedis()

def clearRedis():
  for key in md.client.keys('*'):
    md.client.delete(key)
  check(len(md.client.keys('*')) == 0)

if __name__ == '__main__':
  runTests()
