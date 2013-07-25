"""
    This module handles emailing participants and initiators

    TODO: I'm temporarily logging to the log.txt file. Eventually need to
                replace this with emailing.
"""
import smtplib
import config
from json import dumps

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
    message = 'Participant ' + participant['email'] + ' created.'
    log_stmt = {
        'message': message,
        'links': [
            {
                'href': config.conf['DOMAIN_ROOT'] + participant['vote_link'],
                'text': 'Vote'
            }
        ]
    }
    with open(config.conf['LOG_FILE'], 'a') as fh:
        fh.write(dumps(log_stmt) + '\n')

def emailInitiator(init_email, init_key, poll_key):
    """
    Email the poll's initiator with a link to the poll administration page.

    Args:
        init_email: The initiator's email
        init_key: The initiator's key string
        poll_key: The poll's key string
    """
    # TODO
    message = 'Initiator ' + init_email + ' created.'
    admin_link_path = '/' + poll_key + '/admin?key=' + init_key
    log_stmt = {
        'message': message,
        'links': [
            {
                'href': config.conf['DOMAIN_ROOT'] + admin_link_path,
                'text': 'Administer'
            }
        ]
    }
    with open(config.conf['LOG_FILE'], 'a') as fh:
        fh.write(dumps(log_stmt) + '\n')

def emailResults(poll_key):
    """
    Email the results link to the initator and all participants.
    """
    # TODO
    print 'notify.emailResults() called for ' + poll_key
