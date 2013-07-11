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
    close =  datetime.datetime.strptime( poll_data_raw['close'],
                                         '%Y-%m-%dT%H:%M:%S')
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
