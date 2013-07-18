"""
BallotBox

Author: David Moench
Overview: A polling application.
"""

from flask import Flask, url_for, render_template, request
import config
import model
import helpers
from json import dumps, loads

app = Flask(__name__)

# DB Connect
md = model.Model(config.conf['REDIS_HOST'], config.conf['REDIS_PORT'])

@app.route('/', methods = ['GET', 'POST'])
def indexPage():
  """
  The index page. 'GET' generates a form to describe a new poll.
  'POST' creates the new poll on the DB.
  """
  if request.method == 'GET':
    return render_template('pollcreate.html')
  else: # POST
    poll_data_raw = {}
    for key in request.form:
      poll_data_raw[key] = request.form[key]
    # TODO: Use poll_data_raw from form instead of the following test data
    # once you get front end form set up and validating correctly.
    test_poll_data = {
      'name': 'Favorite Color',
      'choices': ['Red', 'Blue', 'Green', 'Teal'],
      'close': '2015-07-11T04:00:00',
      'participants': ['alouie@gmail.com', 'lluna@gmail.com'],
      'type': 'plurality',
      'initiator': 'david.moench@arc90.com'
    }
    poll_key = md.createPoll(test_poll_data)

    # TODO: Send emails to all participants. Temporarily I will generate the
    # voting links and return them all here
    return dumps(md.getParticipantVoteLinks(poll_key))

@app.route('/<poll_key>/results', methods = ['GET'])
def results(poll_key):
  # Check if poll is ongoing
  poll_data = md.getPoll(poll_key)
  if md.checkPollOngoing(poll_key):
    return 'Results are not available. \'' + poll_data['name'] + '\' is ongoing.'
  else:
    results = md.getAllVotes(poll_key)
    page_data = {}
    page_data['poll'] = poll_data
    page_data['num_participants'] = len(poll_data['participants'])
    page_data['stats'] = helpers.calcStats(results, len(poll_data['choices']))
    # TODO: Initiate deletion of participant and initator data here
    return render_template('results.html', data = page_data)
    # TODO: Remember to handle the case of a tie somewhere

@app.route('/<poll_key>/admin', methods = ['GET'])
def admin(poll_key):
  initiator_key = request.args.get('key')
  poll_data = md.getPoll(poll_key)
  if initiator_key != poll_data['initiator']:
    return render_template('badinitiator.html')
  # TODO: elif poll is over?
  else:
    init_data = md.getInitiator(initiator_key)
    page_data = {}
    page_data['poll'] = poll_data
    return render_template('polladmin.html', data = page_data)

@app.route('/<poll_key>/<participant_key>', methods = ['GET', 'POST', 'PUT'])
def participantPollPage(poll_key, participant_key):
  """
  The participants' voting page. 'GET' generates the participant's ballot.
  'PUT' submits and stores their vote.

  # TODO: Add handler for invalid or expired poll or participant keys
  """
  if request.method == 'GET':
    print participant_key
    if participant_key[:5] != 'part_':
      raise Exception('Invalid participant key.')
    page_data = {}
    page_data['participant'] = md.getParticipant(participant_key)
    page_data['poll'] = md.getPoll(poll_key)
    return render_template('vote.html', data = page_data)
  else: # POST
    # TODO: Reroute to a PUT request to store in Redis. More RESTful.
    md.vote(participant_key, int(request.form['choice']))
    participant = md.getParticipant(participant_key)
    return 'Thank you for voting: ' + participant['email']
    # TODO: Instead redirect back to the vote page but display an alert to the effect of 'Thanks for voting, you can resubmit your vote up until XXXX'.

if __name__ == '__main__':
  app.run(debug = True)
  # To run publicly: app.run(host = '0.0.0.0')
