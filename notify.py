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
import mandrill

def email_participant(participant, poll_data, mandrill_cli):
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
        mandrill_cli: A mandrill API connection object
    """
    try:
        message = {
            'from_email': config.EMAIL_SOURCE,
            'to': [{'email': participant['email']}],
            'subject': 'BallotBox Poll: ' + poll_data['name'],
            'html': ('<p>A BallotBox Poll has been created: ' + poll_data['name'] +
                     '</p><p>' + 'You can vote here: ' + config.DOMAIN_ROOT +
                     participant['vote_link'] + '</p>')
        }
        result = mandrill_cli.messages.send(message = message, async = False)
    except mandrill.Error, e:
        print 'A Mandrill Error Occurred: %s - %s' % (e.__class__, e)
        raise
    # TODO Delete logging when testing is complete
    print 'Participant ' + participant['email'] + ' created.'

def email_initiator(init_email, init_key, poll_key, poll_name, mandrill_cli):
    """
    Email the poll's initiator with a link to the poll administration page.

    Args:
        init_email: The initiator's email
        init_key: The initiator's key string
        poll_key: The poll's key string
        poll_name: Duh
        mandrill_cli: A mandrill API connection object
    """
    admin_link_path = '/' + poll_key + '/admin?key=' + init_key
    try:
        message = {
            'from_email': config.EMAIL_SOURCE,
            'to': [{'email': init_email}],
            'subject': 'BallotBox Poll Created: ' + poll_name,
            'html': ('<p>You created a BallotBox Poll: ' + poll_name +
                    '</p><p>You can administrate it here: ' +
                    config.DOMAIN_ROOT + admin_link_path + '</p>')
        }
        result = mandrill_cli.messages.send(message = message, async = False)
    except mandrill.Error, e:
        print 'A Mandrill Error Occurred: %s - %s' % (e.__class__, e)
        raise

    # TODO Delete logging when testing is complete
    print 'Initiator ' + init_email + ' created.'

def email_results(poll_data, results_link, init_email, mandrill_cli):
    """
    Email the results link to the initator and all participants.

    Args:
        poll_data: A dictionary of poll data. Obtained from model.getPoll()
        results_link: The URL where people can view the poll's results
        init_email: The initiator's email address
        mandrill_cli: A mandrill API connection object

    # TODO: change poll_data scheme so that the initiator record is both the
    # key and email. Then you won't need to pass it around seperately like this.
    """
    poll_name = poll_data['name']
    message = {
        'from_email': config.EMAIL_SOURCE,
        'to': None,
        'subject': 'BallotBox Poll Results: ' + poll_name,
        'html': ('<p>BallotBox poll \'' + poll_name + '\' closed.</p>' +
                 '<p>See the results here: ' + results_link + '</p>')
    }
    # Email all participants
    for part_email in poll_data['participants'].values():
        message['To'] = part_email
        try:
            result = mandrill_cli.messages.send(message = message, async = False)
            print 'EMAILING PARTICIPANT: ' + part_email
        except mandrill.Error, e:
            print 'A Mandrill Error Occurred: %s - %s' % (e.__class__, e)
    # Email initiator
    message['To'] = init_email
    try:
        result = mandrill_cli.messages.send(message = message, async = False)
        print 'EMAILING INITIATOR: ' + init_email
    except mandrill.Error, e:
        print 'A Mandrill Error Occurred: %s - %s' % (e.__class__, e)
        raise
