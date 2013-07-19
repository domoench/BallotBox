"""
  This module handles emailing participants and initiators
"""
import smtplib

def emailParticipant(participant):
  """
  Email the given participant with their ballot link and instructions on how
  to vote.

  Args:
    participant: A dictionary representing a participants email and ballot
      link. For example:
      {
        'email': 'alouie@gmail.com',
        'vote_link': '/poll_0c9a1081760990bcc89ca94bb6bdd5710328f3ef/part_247fd90ba860b79ef41e0770638c69bac98cbd94
      }
  """
  # TODO Implement real emailing
  print participant['email'] + 'has been emailed (not really).'

def emailInitiator(initiator_key):
  """
  Email the poll’s initiator with a link to the poll administration page.
  """
  # TODO

def emailResults(poll_key):
  """
  Email the results link to the initator and all participants.
  """
  # TODO

