"""
    This module handles emailing participants and initiators

    TODO: I'm temporarily logging to the log.txt file. Eventually need to
                replace this with emailing.
"""
import smtplib
from config import conf
import os
from email.mime.text import MIMEText
from json import dumps

smtp_cli = smtplib.SMTP('smtp.mandrillapp.com', 587)
username = os.environ.get('MANDRILL_USER')
password = os.environ.get('MANDRILL_PASS')
smtp_cli.login(username, password)

def email_participant(participant, poll_data):
    """
    Email the given participant with their ballot link and instructions on how
    to vote.

    Args:
        participant: A dictionary representing a participant's email and ballot
            link. For example:
            {
                'email': 'alouie@gmail.com',
                'vote_link': '/poll_MHgzOWVjNmRlYmIwTA/part_MHg0OTM4N2Q0YmNM'
            }
        poll_data: A dictionary of poll data. Obtained from model.getPoll()
    """
    msg = MIMEText('A BallotBox Poll has been created: ' + poll_data['name'] +
                   '\n' + 'You can vote here: ' + conf['DOMAIN_ROOT'] +
                   participant['vote_link'])
    msg['Subject'] = 'BallotBox Poll: ' + poll_data['name']
    msg['From'], msg['To'] = conf['EMAIL_SOURCE'], participant['email']
    smtp_cli.sendmail(msg['From'], msg['To'], msg.as_string())

    # TODO Delete logging when testing is complete
    message = 'Participant ' + participant['email'] + ' created.'
    log_stmt = {
        'message': message,
        'links': [
            {
                'href': conf['DOMAIN_ROOT'] + participant['vote_link'],
                'text': 'Vote'
            }
        ]
    }
    with open(conf['LOG_FILE'], 'a') as fh:
        fh.write(dumps(log_stmt) + '\n')

def email_initiator(init_email, init_key, poll_key, poll_name):
    """
    Email the poll's initiator with a link to the poll administration page.

    Args:
        init_email: The initiator's email
        init_key: The initiator's key string
        poll_key: The poll's key string
    """
    admin_link_path = '/' + poll_key + '/admin?key=' + init_key
    msg = MIMEText('You created a BallotBox Poll: ' + poll_name +
                   '\n' + 'You can administrate it here: ' +
                    conf['DOMAIN_ROOT'] + admin_link_path)
    msg['Subject'] = 'BallotBox Poll Created: ' + poll_name
    msg['From'], msg['To'] = conf['EMAIL_SOURCE'], init_email
    smtp_cli.sendmail(msg['From'], msg['To'], msg.as_string())

    # TODO Delete logging when testing is complete
    message = 'Initiator ' + init_email + ' created.'
    log_stmt = {
        'message': message,
        'links': [
            {
                'href': conf['DOMAIN_ROOT'] + admin_link_path,
                'text': 'Administer'
            }
        ]
    }
    with open(conf['LOG_FILE'], 'a') as fh:
        fh.write(dumps(log_stmt) + '\n')

def email_results(poll_key):
    """
    Email the results link to the initator and all participants.
    """
    # TODO
    print 'notify.email_results() called for ' + poll_key
