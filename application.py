"""

BallotBox

Author: David Moench

Overview: A polling application that is simple and non-invasive for users
    (doesn't require account creation) yet prevents voter fraud like multiple
    voting.

TODO: PEP8 EVERYTHING

"""

from flask import Flask, url_for, render_template, request, redirect
from werkzeug.routing import BaseConverter
import config
import model
import helpers
import notify
import os
from json import dumps, loads

app = Flask(__name__)

# Routing Converters
class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]
app.url_map.converters['regex'] = RegexConverter

# DB Connect
# TODO: Is there a way to do this so it works on Heroku and off?
# 1) Non-Heroku
# md = model.Model(config.REDIS_HOST, int(config.REDIS_PORT))
# 2) Heroku
import urlparse
url = urlparse.urlparse(config.REDISCLOUD_URL)
md = model.Model(host = url.hostname, port = url.port, password = url.password)

@app.route('/', methods = ['GET', 'PUT'])
def index_route():
    """
    The index page. 'GET' generates a form to describe a new poll.
    'PUT' creates the new poll on the DB.
    """
    if request.method == 'GET':
        return render_template('pollcreate.html')
    else: # PUT
        put_data_dict = loads(request.data)
        poll_data_raw = {}
        for key in put_data_dict.keys():
            poll_data_raw[key] = put_data_dict[key]
        poll_key = md.create_poll(poll_data_raw)
        poll_data = md.get_poll(poll_key)
        # Notify the particpants and initiator
        part_link_list = md.get_participant_vote_links(poll_data['participants'], poll_key)
        for part_link in part_link_list:
            notify.email_participant(part_link, poll_data)
        init_key = poll_data['initiator']
        init_data = md.get_initiator(init_key)
        notify.email_initiator(init_data['email'], init_key, poll_key,
                              poll_data['name'])
        # TODO: Delete this notification when testing is complete
        message = 'Poll \'' + poll_data['name'] + '\' created.\n'
        log_stmt = {'message': message, 'links': None}
        with open(config.LOG_FILE, 'a') as fh:
            fh.write(dumps(log_stmt) + '\n')
        # TODO: how to return success?
        return 'success'

@app.route('/<poll_key>/results', methods = ['GET'])
def results_route(poll_key):
    # Check if poll is ongoing
    poll_data = md.get_poll(poll_key)
    if poll_data is None:
        # TODO: Handle better
        return 'Sorry, that poll doesn\'t exist!'
    if md.check_poll_ongoing(poll_key):
        return 'Results are not available. \'' + poll_data['name'] + '\' is ongoing.'
    else:
        # TODO: The following line prevents deleting people's data while letting
        # the results page persist. A possible solution would be to add the calculated
        # stats to the poll data on close.
        results = md.get_all_votes(poll_key)
        percents = helpers.calcStats(results, len(poll_data['choices']))
        percents_readout = {}
        for choice in percents.keys():
            if choice == 'None':
                percents_readout['Did Not Vote'] = round(percents['None'], 2)
            else:
                percents_readout[poll_data['choices'][choice]] = round(percents[choice], 2)
        page_data = {}
        page_data['poll'] = poll_data
        page_data['num_participants'] = len(poll_data['participants'])
        page_data['percents_readout'] = percents_readout
        # TODO: Initiate deletion of participant and initator data here
        return render_template('results.html', data = page_data)
        # TODO: Remember to handle the case of a tie somewhere

@app.route('/<poll_key>/admin', methods = ['GET'])
def admin_route(poll_key):
    init_key = request.args.get('key')
    poll_data = md.get_poll(poll_key)
    # Validate
    page_data = {'link': None}
    no_good = False
    # Check poll exists
    if poll_data is None:
        no_good = True
        page_data['message'] = 'Sorry, that poll doesn\'t exist'
    # Check if the requester is the initiator
    elif init_key != poll_data['initiator']:
        no_good = True
        page_data['message'] = 'Sorry, you don\'t have poll admin creds.'
    # Check poll is ongoing
    elif not md.check_poll_ongoing(poll_key):
        no_good = True
        page_data['message'] = ('Sorry, \'' + poll_data['name'] +
                        '\' has been closed.')
        page_data['link'] = {
            'anchor': config.DOMAIN_ROOT + '/' + poll_key + '/results',
            'text': 'See Results'
        }
    if no_good:
        return render_template('message.html', data = page_data)
    # Ok, we're valid!
    else:
        init_data = md.get_initiator(init_key)
        page_data['poll'] = poll_data
        page_data['poll_key'] = poll_key
        page_data['progress'] = md.get_poll_progress(poll_key)
        page_data['domain_root'] = config.DOMAIN_ROOT
        # Stuff frontend needs easy access to
        page_data['json_data'] = dumps({
          'poll_key': poll_key,
          'init_key': init_key
        })
        return render_template('polladmin.html', data = page_data)

@app.route('/<poll_key>/participants', methods = ['POST'])
def add_participants_route(poll_key):
    # TODO: Rethink this route's return values now that we're getting here
    # via an AJAX request. Same for close route.
    init_key = request.args.get('key')
    poll_data = md.get_poll(poll_key)
    if init_key != poll_data['initiator']:
        page_data = {'link': None}
        page_data['message'] = 'Sorry, you don\'t have poll admin creds.'
        return render_template('message.html', data = page_data)
    else:
        # Add Participants
        new_participants = loads(request.data)
        new_part_map = md.add_poll_participants(poll_key, new_participants)
        # Notify them
        new_part_links_dict = md.get_participant_vote_links(new_part_map, poll_key)
        for participant in new_part_links_dict:
            notify.email_participant(participant, poll_data)
        # TODO: Redirect to admin page with alert that participants were added
        return 'Added Participants! (Not actually though...)'

@app.route('/<poll_key>/status', methods = ['PUT'])
def close_poll_route(poll_key):
    init_key = request.args.get('key')
    poll_data = md.get_poll(poll_key)
    if init_key != poll_data['initiator']:
        page_data = {'link': None}
        page_data['message'] = 'Sorry, you don\'t have poll admin creds.'
        return render_template('message.html', data = page_data)
    else:
        # Close Poll
        md.close_poll(poll_key)
        # Notify People
        message = 'Poll \'' + poll_data['name'] + '\' closed.\n'
        results_link = config.DOMAIN_ROOT + '/' + poll_key + '/results'
        notify.email_results(poll_data, results_link,
                             md.get_initiator(init_key)['email'])

        # TODO remove logging after testing complete
        log_stmt = {
            'message': message,
            'links': [{
                'href': results_link,
                'text': 'See Results'
            }]
        }
        with open(config.LOG_FILE, 'a') as fh:
            fh.write(dumps(log_stmt) + '\n')
        # TODO: Delete people's info
        # TODO: Redirect to results page
        return 'Closed Poll!'

@app.route('/<poll_key>/<regex("part_[a-zA-Z0-9]*"):participant_key>',
           methods = ['GET', 'POST'])
def participant_poll_route(poll_key, participant_key):
    """
    The participants' voting page. 'GET' generates the participant's ballot.
    'PUT' submits and stores their vote.
    """
    poll_data = md.get_poll(poll_key)
    # Validate
    page_data = {'link': None}
    no_good = False
    # Check poll exists
    if poll_data is None:
        no_good = True
        page_data['message'] = 'Sorry, that poll doesn\'t exist'
    # Check requester is a valid participant
    elif participant_key not in poll_data['participants'].keys():
        no_good = True
        page_data['message'] = 'Sorry, you aren\'t a participant of this poll'
    # Check poll is ongoing
    elif not md.check_poll_ongoing(poll_key):
        no_good = True
        page_data['message'] = ('Sorry, \'' + poll_data['name'] +
                                '\' has been closed.')
    if no_good:
        return render_template('message.html', data = page_data)
    # Ok, we're valid!
    if request.method == 'GET':
        page_data['participant'] = md.get_participant(participant_key)
        page_data['poll'] = poll_data
        return render_template('vote.html', data = page_data)
    else: # request.method == POST
        # TODO: Reroute to a PUT request to store in Redis. More RESTful.
        md.vote(participant_key, int(request.form['choice']))
        participant = md.get_participant(participant_key)
        # TODO: Refresh and display an alert to the effect of 'Thanks for
        # voting, you can resubmit your vote up until XXXX'.
        page_data = {}
        page_data['poll'] = md.get_poll(poll_key)
        page_data['participant'] = participant
        page_data['status_msg'] = 'Thank you for voting ' + participant['email']
        return render_template('vote.html', data = page_data)

# TODO: Remove this route after emailing is implemented
@app.route('/log', methods = ['GET'])
def log_route():
    log_lines = []
    with open('log.txt', 'r') as fh:
        for line in fh:
            if line != None:
                line_dict = loads(line)
                log_lines.append(line_dict)
    return render_template('log.html', data = log_lines)

# TODO: Remove this route after emailing is implemented
@app.route('/clearlog', methods = ['GET'])
def clear_log_route():
    md.clear_redis()
    open('log.txt', 'w').close()
    return redirect(url_for('log_route'))

if __name__ == '__main__':
    # app.run(debug = True)
    app.run(host = '0.0.0.0')
