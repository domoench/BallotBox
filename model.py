"""
  Handles interaction between BallotBox Flask app and Redis DB
"""
import redis
import datetime
import helpers
from json import dumps, loads
import config # TODO: Remove this when temporary log file notification is no longer used

class Model:
  def __init__(self, host, port):
    self.host = host
    self.port = port
    self.client = redis.StrictRedis(host = self.host, port = self.port, db = 0)

  def createPoll(self, poll_data_raw):
    """
    Create a new poll record on the DB. Takes a dictionary of poll data,
    generates keys for the poll, initiator, and participants, and stores it
    to the DB.

    Args:
      poll_data_raw: a python dictionary of validated, unprocessed poll data of
        the following form:
        {
          'name': 'Favorite Color',
          'choices': ['Red', 'Blue', 'Green', 'Teal'],
          'close': datetime.datetime(2014, 7, 11, 4, 0).isoformat(),
          'participants': ['alouie@gmail.com', 'lluna@gmail.com'],
          'type': 'plurality',
          'initiator': 'david.moench@arc90.com'
        }

    Returns:
      The created poll's key string. For example:
        'poll_0c9a1081760990bcc89ca94bb6bdd5710328f3ef'
    """
    now = datetime.datetime.utcnow()
    close = datetime.datetime.strptime(poll_data_raw['close'], '%Y-%m-%dT%H:%M:%S')
    ongoing = close - now > datetime.timedelta(minutes = 0)
    init_key = helpers.generateKeyString(poll_data_raw['initiator'],
                                         now.isoformat(), 'init_')
    part_map = {}
    for email in poll_data_raw['participants']:
      part_key = helpers.generateKeyString(email, now.isoformat(), 'part_')
      part_map[part_key] = email
    poll_data_processed = {
      'name': poll_data_raw['name'],
      'choices': poll_data_raw['choices'],
      'ongoing': ongoing,
      'close': poll_data_raw['close'],
      'type': poll_data_raw['type'],
      'initiator': init_key,
      'participants': part_map
    }
    poll_key = helpers.generateKeyString(poll_data_raw['name'], now.isoformat(), 'poll_')
    self.client.set(poll_key, dumps(poll_data_processed))

    # Create initiator's record
    init_data = {
      'email': poll_data_raw['initiator'],
      'poll': poll_key
    }
    self.setInitiator(init_key, init_data)

    # Create participants' records
    for part_key in part_map:
      part_data_raw = {
        'email': part_map[part_key],
        'poll': poll_key,
        'voted': False,
        'choice': None
      }
      self.setParticipant(part_key, part_data_raw)

    return poll_key

  def setInitiator(self, init_key, init_data_raw):
    """
    Create a new, or set an existing, Initiator record on the DB.

    Args:
      init_key: The initiator's key string. For Example:
        init_4dc6297e78836e8a5c48b0deb3b7cf3ace70b300
      init_data_raw:  a python dictionary of validated, unprocessed initiator
        data of the following form:
        {
          'email': 'david.moench@arc90.com',
          'poll': 'poll_0c9a1081760990bcc89ca94bb6bdd5710328f3ef'
        }

    Returns:
      The initiator's key string.
    """
    self.client.set(init_key, dumps(init_data_raw))
    return init_key

  def setParticipant(self, part_key, part_data_raw):
    """
    Create a new Participant record on the DB.

    Args:
      part_key: The participant's key string. For Example:
        'part_247fd90ba860b79ef41e0770638c69bac98cbd94'
      part_data_raw: a python dictionary of validated, unprocessed participant
        data of the following form:
        {
          'email': 'alouie@gmail.com',
          'poll': 'poll_0c9a1081760990bcc89ca94bb6bdd5710328f3ef',
          'voted': True,
          'choice': 1
        }
        Note: If 'voted' is False, 'choice' should be None

    Returns:
      The participant's key string.
    """
    self.client.set(part_key, dumps(part_data_raw))
    return part_key

  def getPoll(self, poll_key):
    """
    Get and JSON decode a poll record.

    Args:
      poll_key: The poll's key string.

    Returns:
      A python dictionary of the record.
    """
    if poll_key[:5] != 'poll_':
      raise Exception('Incorrect key passed to getPoll(): ' + poll_key)
    return loads(self.client.get(poll_key))

  def getParticipant(self, part_key):
    """
    Get and JSON decode a participant record.

    Args:
      part_key: The participant's key string.

    Returns:
      A python dictionary of the record.
    """
    if part_key[:5] != 'part_':
      raise Exception('Incorrect key passed to getPartiticpant(): ' + part_key)
    return loads(self.client.get(part_key))

  def getInitiator(self, init_key):
    """
    Get and JSON decode a initiator record.

    Args:
      init_key: The initiator's key string.

    Returns:
      A python dictionary of the record.
    """
    if init_key[:5] != 'init_':
      raise Exception('Incorrect key passed to model.getInitiator(): ' +
                      init_key)
    print loads(self.client.get(init_key))
    return loads(self.client.get(init_key))

  def vote(self, part_key, choice):
    """
    Set the participant record's 'choice' attribute and set its 'voted'
    attribute to True.

    Args:
      part_key: The participant's key string.
      choice: An integer offset into the parent poll's 'choices' list

    Return:
      The participant data dictionary.
    """
    part_data = self.getParticipant(part_key)
    poll_key = part_data['poll']
    poll_data = self.getPoll(poll_key)
    num_choices = len(poll_data['choices'])
    if(choice not in range(num_choices)):
      raise Exception('Invalid choice value ' + choice + ' provided to model.vote()')
    part_data['choice'] = choice
    part_data['voted'] = True
    self.setParticipant(part_key, part_data)
    # TODO: Remove the following notification after the demo
    message = 'Participant ' + part_data['email'] + ' voted.'
    log_stmt = {'message': message, 'links': None}
    with open(config.conf['LOG_FILE'], 'a') as fh:
      fh.write(dumps(log_stmt) + '\n')
    # Check if this was the last vote needed
    if not self.checkPollOngoing(poll_key):
      self.closePoll(poll_key)
    return part_data

  def addPollParticipants(self, poll_key, new_participants):
    """
    Add new participants to an ongoing poll.

    Args:
      poll_key: The poll's key string.
      new_participants: A List of well-formed participant email strings.

    Returns:
      A map of key:email pairs for newly added participants. For example:
      {
        'part_247fd90ba860b79ef41e0770638c69bac98cbd94': 'alouie3@gmail.com',
        'part_0c9a1081760990bcc89ca94bb6bdd5710328f3ef': 'lluna@gmail.com'
      }
    """
    poll_data = self.getPoll(poll_key)
    participants = poll_data['participants']
    part_emails = participants.values()
    now_str = datetime.datetime.utcnow().isoformat()

    new_part_map = {}
    for email in new_participants:
      if email not in part_emails: # No duplicate emails
        # Add new participant key to the Poll
        new_part_key = helpers.generateKeyString(email, now_str, 'part_')
        participants[new_part_key] = email
        self.client.set(poll_key, dumps(poll_data))
        # Create new participant record
        new_part_data_raw = {
          'email':  email,
          'poll': poll_key,
          'voted': False,
          'choice': None
        }
        self.setParticipant(new_part_key, new_part_data_raw)
        new_part_map[new_part_key] = email
    return new_part_map

  def checkPollOngoing(self, poll_key):
    """
    Checks if the poll is still ongoing (meaning there is still time left and
    there are participants who have not voted). If the poll's 'ongoing'
    attribute is True, but we find that there is no time remaining or everyone
    has voted then we call closePoll().

    Args:
      poll_key: The poll's key string.

    Returns:
      Boolean. True if there is still time left in the poll and there are still
      participants who have not voted. False otherwise.
    """
    poll_data = self.getPoll(poll_key)
    now = datetime.datetime.utcnow()
    close = datetime.datetime.strptime(poll_data['close'], '%Y-%m-%dT%H:%M:%S')
    time_remains = close - now > datetime.timedelta(minutes = 0)
    if not poll_data['ongoing']:
      return False
    if not time_remains:
      # self.closePoll(poll_key)
      return False
    for part_key in poll_data['participants'].keys():
      part_data = self.getParticipant(part_key)
      if part_data['voted'] == False:
        return True
    # All participants have voted
    # self.closePoll(poll_key)
    return False

  def closePoll(self, poll_key):
    """
    Sets the poll's 'ongoing' field to False

    Args:
      poll_key: The poll's key string.
    """
    poll_data = self.getPoll(poll_key)
    poll_data['ongoing'] = False
    self.client.set(poll_key, dumps(poll_data))
    # TODO: Notify the participants and send them the results: notify.emailResults()

  def getAllVotes(self, poll_key):
    """
    Returns a list of all participants' choices.

    Args:
      poll_key: The poll's key string.

    Returns:
      A list where each element is one participant's integer choice
    """
    poll_data = self.getPoll(poll_key)
    part_keys = poll_data['participants']
    results = []
    for part_key in part_keys:
      part_choice = self.getParticipant(part_key)['choice']
      results.append(part_choice)
    return results

  def deletePollPeople(self, poll_data):
    """
    Deletes the Initiator's and all Participants' DB records for the given
    poll.

    Args:
      poll_data: The poll's data dictionary.
    """
    # Delete Initator and Participant data
    self.deletePerson(poll_data['initiator'])
    for part_key in poll_data['participants'].keys():
      self.deletePerson(part_key)

  def deletePerson(self, key):
    """
    Delete a participant or initiator record.

    Args:
      key: The particpant or initator key string
    """
    if key[:5] not in ['part_', 'init_']:
      raise Exception('model.deletePerson() can only be performed on a' +
                      'participant or initiator record.')
    # TODO: Delete this notification after testing is complete
    if key[:5] == 'part_':
      print 'PARTICIPANT: ', self.getParticipant(key)['email']
      message = 'Participant ' + self.getParticipant(key)['email'] + ' deleted.'
    else:
      print 'INITIATOR: ', self.getInitiator(key)
      message = 'Initiator ' + self.getInitiator(key)['email'] + ' deleted.'
    log_stmt = {'message': message, 'links': None}
    with open('log.txt', 'a') as fh:
      fh.write(dumps(log_stmt) + '\n')
    # Delete the DB record
    self.client.delete(key)

  def getParticipantVoteLinks(self, participants, poll_key):
    """
    Gets a list of participant email/vote-link pairs.

    Args:
      poll_key: The key string for the poll to which the participants belong.
      participants: A map of participant keys to emails. For example:
        {
          'part_247fd90ba860b79ef41e0770638c69bac98cbd94': 'alouie3@gmail.com',
          'part_0c9a1081760990bcc89ca94bb6bdd5710328f3ef': 'lluna@gmail.com'
        }

    Returns:
      A list of participant email/vote-link pair dictionaries. For example:
      [
        {
          'email': 'alouie@gmail.com',
          'vote_link': '/poll_0c9a1081760990bcc89ca94bb6bdd5710328f3ef/part_247fd90ba860b79ef41e0770638c69bac98cbd94
        },
        {
          'email': 'lluna@gmail.com',
          'vote_link': '/poll_0c9a1081760990bcc89ca94bb6bdd5710328f3ef/part_9b55ce38e1074928830b37bda5ddf325ac70a3d7
        }
      ]
    """
    result = []
    for part_key in participants.keys():
      participant_pair = {
        'email': participants[part_key],
        'vote_link': '/' + poll_key + '/' + part_key
      }
      result.append(participant_pair)
    return result

  def getPollProgress(self, poll_key):
    """
    Return a tuple of the number of people who have voted and the number of
    poll participants

    Args:
      poll_key: The poll's key string.

    Returns:
      A tuple of integers of the the following form:
      (num_participants_voted, num_particpants)
    """
    poll_data = self.getPoll(poll_key)
    part_keys = poll_data['participants'].keys()
    num_participants = len(part_keys)
    num_voted = 0
    for part_key in part_keys:
      part_data = self.getParticipant(part_key)
      if part_data['voted']:
        num_voted += 1
    return (num_voted, num_participants)

  def clearRedis(self):
    for key in self.client.keys('*'):
      self.client.delete(key)
