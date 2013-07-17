"""
BallotBox

Author: David Moench
Overview: A polling application.
"""

from flask import Flask, url_for, render_template, request
import config
import model
from json import dumps, loads

app = Flask(__name__)

# DB Connect
md = model.Model(config.conf['HOST'], config.conf['PORT'])

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

@app.route('/<poll_key>/<participant_key>', methods = ['GET', 'PUT'])
def participantPollPage(poll_key, participant_key):
  """
  The participants' voting page. 'GET' generates the participant's ballot.
  'PUT' submits and stores their vote.
  """
  if request.method == 'GET':
    if participant_key[:5] != 'part_':
      raise Exception('Invalid participant key.')
    page_data = {}
    page_data['participant'] = md.getParticipant(participant_key)
    page_data['poll'] = md.getPoll(poll_key)
    return render_template('vote.html', data = page_data)
  else:
    # TODO
    return 'Not written yet!'

if __name__ == '__main__':
  app.run(debug = True)
  # To run publicly: app.run(host = '0.0.0.0')
