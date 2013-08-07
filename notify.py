"""
    This module handles emailing participants and initiators

    TODO: I'm temporarily logging to the log.txt file. Eventually need to
                replace this with emailing.
"""
import smtplib
import config
import os
from email.mime.text import MIMEText
from json import dumps

smtp_cli = smtplib.SMTP('smtp.mandrillapp.com', 587)
smtp_cli.login(config.MANDRILL_USER, config.MANDRILL_PASS)

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
                   '\n' + 'You can vote here: ' + config.DOMAIN_ROOT +
                   participant['vote_link'])
    msg['Subject'] = 'BallotBox Poll: ' + poll_data['name']
    msg['From'], msg['To'] = config.EMAIL_SOURCE, participant['email']
    smtp_cli.sendmail(msg['From'], msg['To'], msg.as_string())

    # TODO Delete logging when testing is complete
    message = 'Participant ' + participant['email'] + ' created.'
    log_stmt = {
        'message': message,
        'links': [
            {
                'href': config.DOMAIN_ROOT + participant['vote_link'],
                'text': 'Vote'
            }
        ]
    }
    with open(config.LOG_FILE, 'a') as fh:
        fh.write(dumps(log_stmt) + '\n')

def email_initiator(init_email, init_key, poll_key, poll_name):
    """
    Email the poll's initiator with a link to the poll administration page.

    Args:
        init_email: The initiator's email
        init_key: The initiator's key string
        poll_key: The poll's key string
        poll_name: Duh
    """
    admin_link_path = '/' + poll_key + '/admin?key=' + init_key
    msg = MIMEText('You created a BallotBox Poll: ' + poll_name +
                   '\n' + 'You can administrate it here: ' +
                    config.DOMAIN_ROOT + admin_link_path)
    msg['Subject'] = 'BallotBox Poll Created: ' + poll_name
    msg['From'], msg['To'] = config.EMAIL_SOURCE, init_email
    smtp_cli.sendmail(msg['From'], msg['To'], msg.as_string())

    # TODO Delete logging when testing is complete
    message = 'Initiator ' + init_email + ' created.'
    log_stmt = {
        'message': message,
        'links': [
            {
                'href': config.DOMAIN_ROOT + admin_link_path,
                'text': 'Administer'
            }
        ]
    }
    with open(config.LOG_FILE, 'a') as fh:
        fh.write(dumps(log_stmt) + '\n')

def email_results(poll_data, results_link, init_email):
    """
    Email the results link to the initator and all participants.

    Args:
        poll_data: A dictionary of poll data. Obtained from model.getPoll()
        results_link: The URL where people can view the poll's results
        init_email: The initiator's email address

    # TODO: change poll_data scheme so that the initiator record is both the
    # key and email. Then you won't need to pass it around seperately like this.
    """
    poll_name = poll_data['name']
    msg = MIMEText('BallotBox poll \'' + poll_name + '\' closed.\n' +
                   'See the results here: ' + results_link)
    msg['Subject'] = 'BallotBox Poll Results: ' + poll_name
    msg['From'] = config.EMAIL_SOURCE
    # Email all participants
    for part_email in poll_data['participants'].values():
        print 'EMAILING PARTICIPANT: ' + part_email
        msg['To'] = part_email
        smtp_cli.sendmail(msg['From'], msg['To'], msg.as_string())
    # Email initiator
    msg['To'] = init_email
    print 'EMAILING INITIATOR: ' + init_email
    smtp_cli.sendmail(msg['From'], msg['To'], msg.as_string())
