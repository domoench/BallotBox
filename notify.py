"""
  This module handles emailing participants and initiators

  TODO: I'm temporarily logging to the log.txt file. Eventually need to
        replace this with emailing.
"""
import smtplib
import config

def emailParticipant(participant):
  """
  Email the given participant with their ballot link and instructions on how
  to vote.

  Args:
    participant: A dictionary representing a participant's email and ballot
      link. For example:
      {
        'email': 'alouie@gmail.com',
        'vote_link': '/poll_f6a1fd2b72d5a5a9ab353e9332436729e75c2855cb3cf4a67fb9d70408b893bb/part_b8618807445dc133e507518a053aadc6fc75dd998f24b2dc9350c5b659c6efc6
      }
  """
  # TODO Implement real emailing
  f = open(config.conf['LOG_FILE'], 'a')
  f.write('Participant ' + participant['email'] + ' can vote at: <' +
          participant['vote_link'] + '>\n')
  f.close()

def emailInitiator(init_email, init_key, poll_key):
  """
  Email the poll's initiator with a link to the poll administration page.

  Args:
    init_email: The initiator's email
    init_key: The initiator's key string
    poll_key: The poll's key string
  """
  # TODO
  f = open(config.conf['LOG_FILE'], 'a')
  f.write('Initiator ' + init_email + ' can administrate at: </' + poll_key +
          '/admin?key=' + init_key)
  f.close()

def emailResults(poll_key):
  """
  Email the results link to the initator and all participants.
  """
  # TODO
  print 'notify.emailResults() called for ' + poll_key
