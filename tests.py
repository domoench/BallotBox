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
from json import dumps, loads
import random
import math
import smtplib
from email.mime.text import MIMEText
import os

# DB Connection
md = model.Model(config.REDIS_HOST, int(config.REDIS_PORT))

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
    test_redis()
    test_create_and_get_poll()
    test_create_and_get_initiator()
    test_create_and_get_participant()
    test_no_duplicate_participants()
    test_add_poll_participants()
    test_vote()
    test_check_poll_ongoing()
    # test_close_poll() TODO
    # test_delete_poll_people() TODO
    test_calc_stats()
    test_get_all_votes()
    test_get_participant_vote_links()
    test_get_poll_progress()
    test_delete_person()
    test_smtp()
    md.clear_redis()
    print 'All tests passed!'

def check(predicate):
    if not predicate:
        raise Exception('Check failed')

def test_redis():
    client = redis.StrictRedis(host = config.REDIS_HOST,
                               port = int(config.REDIS_PORT), db = 0)
    client.set('v1', 'test value 1')
    check(client.get('v1') == 'test value 1')
    client.delete('v1')
    check(client.get('v1') == None)

# TODO: Form Parsing Tests

def test_create_and_get_initiator():
    now_str = datetime.datetime.utcnow().isoformat()
    poll_key = helpers.generateKeyString(poll_data_raw['name'], 'poll_')
    init_key = helpers.generateKeyString(poll_data_raw['initiator'],
                                         'init_')
    init_data_raw = {
        'email': poll_data_raw['initiator'],
        'poll': poll_key
    }
    # Insert then Check
    md.set_initiator(init_key, init_data_raw)
    init_data = md.get_initiator(init_key)
    check(init_data['email'] == poll_data_raw['initiator'])
    check(init_data['poll'] == poll_key)
    # Fake Initiator
    check(md.get_initiator('init_fakeparticipant') == None)
    md.clear_redis()

def test_create_and_get_participant():
    now_str = datetime.datetime.utcnow().isoformat()
    poll_key = helpers.generateKeyString(poll_data_raw['name'], 'poll_')
    part_key = helpers.generateKeyString(poll_data_raw['participants'][0],
                                                       'part_')
    part_data_raw = {
        'email': poll_data_raw['participants'][0],
        'poll': poll_key,
        'voted': True,
        'choice': 1
    }
    # Insert then Check
    md.set_participant(part_key, part_data_raw)
    part_data = md.get_participant(part_key)
    check(part_data['email'] == poll_data_raw['participants'][0])
    check(part_data['poll'] == poll_key)
    check(part_data['voted'] == True)
    check(part_data['choice'] == 1)
    # Fake Participant
    check(md.get_participant('part_fakeparticipant') == None)
    md.clear_redis()

def test_create_and_get_poll():
    # Fake Poll
    check(md.get_poll('poll_fakeyfake') == None)
    # Real Poll
    poll_key = md.create_poll(poll_data_raw)
    poll_data = md.get_poll(poll_key)
    check(poll_data['name'] == name)
    check(poll_data['choices'] == choices)
    check(poll_data['close'] == close)
    check(poll_data['type'] == poll_type)
    # Look up initiator info from poll
    init_key = poll_data['initiator']
    init_data = md.get_initiator(init_key)
    check(init_data['email'] == poll_data_raw['initiator'])
    check(init_data['poll'] == poll_key)

    # Look up participants info from poll
    num_participants = len(poll_data_raw['participants'])
    key_count = 0
    for part_key in poll_data['participants']:
        key_count += 1
        part_data = md.get_participant(part_key)
        check(part_data['poll'] == poll_key)
        check(part_data['email'] in poll_data_raw['participants'])
    check(num_participants == key_count)
    # Look up poll from initiator
    check(poll_data == md.get_poll(init_data['poll']))
    # Look up poll from participant
    check(poll_data == md.get_poll(part_data['poll']))
    md.clear_redis()

def test_vote():
    poll_key = md.create_poll(poll_data_raw)
    poll_data = md.get_poll(poll_key)
    for part_key in poll_data['participants']:
        participant = md.vote(part_key, 0)
        choice = participant['choice']
        check(choice == 0)
        check(participant['voted'] == True)
        check(poll_data['choices'][choice] == poll_data_raw['choices'][choice])
    md.clear_redis()

def test_add_poll_participants():
    poll_key = md.create_poll(poll_data_raw)
    # Insert
    new_participants = []
    for i in range(0, 300):
        new_participants.append(str(i) + '@gmail.com')
    new_part_keys = md.add_poll_participants(poll_key, new_participants)
    # Check
    poll_participants = md.get_poll(poll_key)['participants']
    for part_key in poll_participants.keys():
        part_data = md.get_participant(part_key)
        check(part_data['choice'] == None)
        check(part_data['poll'] == poll_key)
        check(part_data['voted'] == False)
        check(part_data['email'] == poll_participants[part_key])
    check(len(new_part_keys) == len(new_participants))
    md.clear_redis()

def test_no_duplicate_participants():
    # Poll Creation ignores duplicates
    pd_raw = {
        'name': 'a',
        'choices': ['a', 'b', 'c'],
        'close': datetime.datetime(2015, 7, 11, 4, 0).isoformat(),
        'participants': ['a@b.com', 'a@b.com'],
        'type': 'plurality',
        'initiator': 'init@b.com'
    }
    poll_key = md.create_poll(pd_raw)
    participants = md.get_poll(poll_key)['participants']
    check(len(participants.keys()) == 1)
    # Participant Addition ignores duplicates
    new_participants = ['a@b.com', 'c@d.com']
    new_part_keys = md.add_poll_participants(poll_key, new_participants)
    check(len(new_part_keys) == 1)
    check(len(md.get_poll(poll_key)['participants'].keys()) == 2)
    md.clear_redis()

def test_check_poll_ongoing():
    # Ongoing
    poll1_key = md.create_poll(poll_data_raw)
    check(md.check_poll_ongoing(poll1_key))
    poll1_data = md.get_poll(poll1_key)
    check(poll1_data['ongoing'] == True)
    # Ongoing, though all participants have voted
    poll2_key = md.create_poll(poll_data_raw)
    poll2_data = md.get_poll(poll2_key)
    poll2_part_keys = poll2_data['participants'].keys()
    for part_key in poll2_part_keys:
        md.vote(part_key, 0)
    check(md.check_poll_ongoing(poll2_key))
    # Ongoing, but time is up
    poll3_key = md.create_poll(poll_data_raw)
    poll3_data = md.get_poll(poll3_key)
    poll3_data['close'] = datetime.datetime(1987, 5, 20, 4, 0).isoformat()
    md.client.set(poll3_key, dumps(poll3_data))
    check(not md.check_poll_ongoing(poll3_key))
    md.clear_redis()

def test_calc_stats():
    results1 = helpers.calcStats([0, 3, 2, 1, 1, 0, 1, 0, 1, 3], 4)
    expected1 = {0: 30, 1: 40, 2: 10, 3: 20, 'None': 0}
    check(results1 == expected1)
    results2 = helpers.calcStats([0, 1, 2, None, None], 3)
    expected2 = {0: 20, 1: 20, 2: 20, 'None': 40}

# This basically simulates the lifecycle of an entire vote
def test_get_all_votes():
    poll_key = md.create_poll(poll_data_raw)
    # Insert
    new_participants = []
    for i in range(0, 100):
        new_participants.append(str(i) + '@gmail.com')
    md.add_poll_participants(poll_key, new_participants)
    # Vote
    participants = md.get_poll(poll_key)['participants']
    for part_key in participants:
        md.vote(part_key, random.randint(0, 3))
    md.close_poll(poll_key)
    poll_data = md.get_poll(poll_key)
    check(len(poll_data['participants']) == 102)
    choices_list = md.get_all_votes(poll_key)
    results = helpers.calcStats(choices_list, 4)
    total_percent = 0
    for key in results:
        total_percent += results[key]
    check(math.fabs(total_percent - 100.0) < 0.00001)
    md.clear_redis()

def test_delete_person():
    poll_key = md.create_poll(poll_data_raw)
    participants = md.get_poll(poll_key)['participants']
    for part_key in participants:
        md.delete_person(part_key)
    md.delete_person(md.get_poll(poll_key)['initiator'])
    # Only the poll record remains
    check(len(md.client.keys('*')) == 1)
    md.clear_redis()

def test_smtp():
    from_addr = 'david.moench@arc90.com'
    to_addr = 'david.moench@arc90.com'
    msg = MIMEText('The BallotBox test suite generated this email. Yay')
    msg['Subject'] = 'BallotBox Test Email'
    msg['From'], msg['To'] = from_addr, to_addr
    # Make SMTP connection through mandrill
    s = smtplib.SMTP('smtp.mandrillapp.com', 587)
    username = config.MANDRILL_USER
    password = config.MANDRILL_PASS
    s.login(username, password)
    s.sendmail(msg['From'], msg['To'], msg.as_string())
    s.quit()

def test_get_participant_vote_links():
    poll_key = md.create_poll(poll_data_raw)
    new_participants = []
    for i in range(0, 100):
        new_participants.append(str(i) + '@gmail.com')
    added = md.add_poll_participants(poll_key, new_participants)
    check(len(added) == 100)
    poll_data = md.get_poll(poll_key)
    results = md.get_participant_vote_links(poll_data['participants'], poll_key)
    for pair in results:
        vote_link = pair['vote_link']
        link_segs = vote_link.split('/')
        check(link_segs[-1] in poll_data['participants'])
        check(link_segs[-2] == poll_key)
    md.clear_redis()

def test_get_poll_progress():
    poll_key = md.create_poll(poll_data_raw)
    # Insert
    new_participants = []
    for i in range(0, 50):
        new_participants.append(str(i) + '@gmail.com')
    md.add_poll_participants(poll_key, new_participants)
    # Vote
    part_keys = md.get_poll(poll_key)['participants'].keys()
    for part_key in part_keys[:25]:
        md.vote(part_key, random.randint(0, 3))
    prog_tuple = md.get_poll_progress(poll_key)
    check(prog_tuple == (25, 52))
    md.clear_redis()

if __name__ == '__main__':
    runTests()
