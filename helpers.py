"""
  BallotBox Helper Functions.

  TODO: Seperate these out into sensible modules
"""

import hashlib

def generateKeyString(seed, time_now, prefix):
  """
  Generates a unique key that will be used in Redis to identify poll,
  initiator, and participant records.

  Args:
    seed: A hash seed string
    time_now: A time string generated by datetime.datetime.utcnow().isoformat()
    prefix: A string to identify the key as IDing a poll, initiator, or
      participant record.
  """
  if prefix not in ['poll_', 'init_', 'part_']:
    raise Exception('Invalid key prefix: ' + prefix)
  hash_token = hashlib.sha256(seed + time_now).hexdigest()
  return prefix + hash_token

