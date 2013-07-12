"""
  Handles interaction between BallotBox Flask app and Redis DB
"""
import redis
import datetime
import helpers
import json

class Model:
  def __init__( self, host, port ):
    self.host = host
    self.port = port
    self.client = redis.StrictRedis( host = self.host, port = self.port, db = 0 )

  def createPoll( self, poll_data_raw ):
    """
    Create a new poll record on the DB. Takes a dictionary of poll data,
    generates keys for the poll, initiator, and participants, and stores it
    to the DB.

    Args:
      poll_data_raw: a python dictionary of validated, unprocessed poll data of
        the following form:
        {
          'name': 'Favorite Color',
          'choices': [ 'Red', 'Blue', 'Green', 'Teal' ],
          'close': datetime.datetime(2014, 7, 11, 4, 0).isoformat(),
          'participants': [ 'alouie@gmail.com', 'lluna@gmail.com' ],
          'type': 'majority',
          'initiator': 'david.moench@arc90.com'
        }

    Returns:
      The created poll's key string. For example:
        'poll_0c9a1081760990bcc89ca94bb6bdd5710328f3ef'
    """
    now = datetime.datetime.utcnow()
    close = datetime.datetime.strptime( poll_data_raw['close'], '%Y-%m-%dT%H:%M:%S')
    ongoing = close - now > datetime.timedelta( minutes = 0 )
    poll_data_processed = {
      'name': poll_data_raw[ 'name' ],
      'choices': poll_data_raw[ 'choices' ],
      'ongoing': ongoing,
      'close': poll_data_raw[ 'close' ],
      'type': poll_data_raw[ 'type' ],
      'initiator': helpers.generateKeyString( poll_data_raw['initiator'], now.isoformat(), 'init_' ),
      'participants': [
        helpers.generateKeyString( poll_data_raw['participants'][0], now.isoformat(), 'part_' ),
        helpers.generateKeyString( poll_data_raw['participants'][1], now.isoformat(), 'part_' )
      ]
    }
    poll_key = helpers.generateKeyString( poll_data_raw['name'], now.isoformat(), 'poll_' )
    self.client.set( poll_key, json.dumps(poll_data_processed) )
    return poll_key

  def createInitiator( self, init_key, init_data_raw ):
    """
    Create a new Initiator record on the DB.

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
      The created initiator's key string.
    """
    self.client.set( init_key, json.dumps(init_data_raw) )
    return init_key

  def createParticipant( self, part_key, part_data_raw ):
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
      The created participant's key string.
    """
    self.client.set( part_key, json.dumps(part_data_raw) )
    return part_key

  def getPoll( self, poll_key ):
    """
    Get and JSON decode a poll record.

    Args:
      poll_key: The poll's key string.

    Returns:
      A python dictionary of the record.
    """
    if poll_key[:5] != 'poll_':
      raise Exception( 'Incorrect key passed to getPoll(): ' + poll_key )
    return json.loads( self.client.get(poll_key) )

  def getParticipant( self, part_key ):
    """
    Get and JSON decode a participant record.

    Args:
      part_key: The participant's key string.

    Returns:
      A python dictionary of the record.
    """
    if part_key[:5] != 'part_':
      raise Exception( 'Incorrect key passed to getPartiticpant(): ' + part_key )
    return json.loads( self.client.get(part_key) )

  def getInitiator( self, init_key ):
    """
    Get and JSON decode a initiator record.

    Args:
      init_key: The initiator's key string.

    Returns:
      A python dictionary of the record.
    """
    if init_key[:5] != 'init_':
      raise Exception( 'Incorrect key passed to getInitiator(): ' + init_key )
    return json.loads( self.client.get(init_key) )
