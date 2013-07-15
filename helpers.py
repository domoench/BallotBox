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

def calcStats(choices_list, num_choices):
  """
  Calculate the percentage breakdown between the choices in the given choices
  list

  Args:
    choices_list: A list where each element is one participant's integer choice.
      For example: [0, 3, 2, 1, 1, 0, 1, 0, 1, 3]
    num_choices: The number of choices in the vote.

  Returns:
    A dictionary mapping each choice to its percentage of the total vote. For
    example: {0: 30, 1: 40, 2: 10, 3: 20}
  """
  num_votes = len(choices_list)
  stats = {}
  for i in range(0, num_choices):
    stats[i] = 0
  # Tally up votes
  for choice in choices_list:
    stats[choice] += 1
  # Convert to percentage
  for key in stats:
    stats[key] = (stats[key] / float(num_votes)) * 100
  return stats
