"""

BallotBox

Author: David Moench

Overview: A polling application that is simple and non-invasive for users
  (doesn't require account creation) yet prevents voter fraud like multiple
  voting.

TODO: PEP8 EVERYTHING

"""

from flask import Flask, url_for, render_template, request, redirect
import config
import model
import helpers
import notify
from json import dumps, loads

app = Flask(__name__)

# DB Connect
md = model.Model(config.conf['REDIS_HOST'], config.conf['REDIS_PORT'])

@app.route('/', methods = ['GET', 'POST'])
def index_page():
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
    poll_data = md.getPoll(poll_key)
    # Notify the partiicpants and initiator
    part_link_list = md.getParticipantVoteLinks(poll_data['participants'], poll_key)
    for part_link in part_link_list:
      notify.emailParticipant(part_link)
    init_key = poll_data['initiator']
    init_data = md.getInitiator(init_key)
    notify.emailInitiator(init_data['email'], init_key, poll_key)
    # TODO: Delete this notification when testing is complete
    message = 'Poll \'' + poll_data['name'] + '\' created.\n'
    log_stmt = {'message': message, 'links': None}
    with open(config.conf['LOG_FILE'], 'a') as fh:
      fh.write(dumps(log_stmt) + '\n')
    # TODO: Change to redirect to admin page after testing is complete.
    return redirect(url_for('logDisplay'))

@app.route('/<poll_key>/results', methods = ['GET'])
def results(poll_key):
  # Check if poll is ongoing
  poll_data = md.getPoll(poll_key)
  if poll_data is None:
    # TODO: Handle better
    return 'Sorry, that poll doesn\'t exist!'
  if md.checkPollOngoing(poll_key):
    return 'Results are not available. \'' + poll_data['name'] + '\' is ongoing.'
  else:
    # TODO: The following line prevents deleting people's data while letting
    # the results page persist. A possible solution would be to add the calculated
    # stats to the poll data on close.
    results = md.getAllVotes(poll_key)
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

@app.route('/<poll_key>/<participant_key>', methods = ['GET', 'POST', 'PUT'])
def participantPollPage(poll_key, participant_key):
  """
  The participants' voting page. 'GET' generates the participant's ballot.
  'PUT' submits and stores their vote.
  """
  if request.method == 'GET':
    poll_data = md.getPoll(poll_key)
    # Check poll is ongoing
    if not md.checkPollOngoing(poll_key):
      page_data = {}
      page_data['poll_key'] = poll_key
      page_data['poll'] = poll_data
      page_data['domain_root'] = config.conf['DOMAIN_ROOT']
      return render_template('pollclosed.html', data = page_data)
    # Check valid participant
    if participant_key not in poll_data['participants'].keys():
      raise Exception('Invalid participant key.')
    page_data = {}
    page_data['participant'] = md.getParticipant(participant_key)
    page_data['poll'] = poll_data
    return render_template('vote.html', data = page_data)
  else: # request.method == POST
    # TODO: Reroute to a PUT request to store in Redis. More RESTful.
    md.vote(participant_key, int(request.form['choice']))
    participant = md.getParticipant(participant_key)
    # TODO: Refresh and display an alert to the effect of 'Thanks for voting, you can resubmit your vote up until XXXX'.
    page_data = {}
    page_data['poll'] = md.getPoll(poll_key)
    page_data['participant'] = participant
    page_data['status_msg'] = 'Thank you for voting ' + participant['email']
    return render_template('vote.html', data = page_data)

@app.route('/<poll_key>/admin', methods = ['GET'])
def admin(poll_key):
  init_key = request.args.get('key')
  poll_data = md.getPoll(poll_key)
  if poll_data is None:
    # TODO: Handle better
    return 'Sorry, that poll doesn\'t exist!'
  if init_key != poll_data['initiator']:
    return render_template('badinitiator.html')
  # Check poll is ongoing
  if not md.checkPollOngoing(poll_key):
    page_data = {}
    page_data['poll_key'] = poll_key
    page_data['poll'] = poll_data
    page_data['domain_root'] = config.conf['DOMAIN_ROOT']
    return render_template('pollclosed.html', data = page_data)
  else:
    init_data = md.getInitiator(init_key)
    page_data = {}
    page_data['poll'] = poll_data
    page_data['poll_key'] = poll_key
    page_data['progress'] = md.getPollProgress(poll_key)
    page_data['domain_root'] = config.conf['DOMAIN_ROOT']
    return render_template('polladmin.html', data = page_data)

@app.route('/<poll_key>/add', methods = ['POST'])
def addParticipants(poll_key):
  # TODO: Reroute to a PATCH request to store in Redis. More RESTful.
  init_key = request.args.get('key')
  poll_data = md.getPoll(poll_key)
  if init_key != poll_data['initiator']:
    return render_template('badinitiator.html')
  else:
    # Add Participants
    # TODO replace the dummy new_particpants data with data passed in from the admin page form.
    new_participants = []
    for i in range(0, 10):
      new_participants.append('dummy' + str(i) + '@gmail.com')
    new_part_map = md.addPollParticipants(poll_key, new_participants)
    # Notify them
    new_part_links_dict = md.getParticipantVoteLinks(new_part_map, poll_key)
    for participant in new_part_links_dict:
      notify.emailParticipant(participant)
    # TODO: Redirect to admin page with alert that participants were added
    return 'Added Participants! (Not actually though...)'

@app.route('/<poll_key>/close', methods = ['POST'])
def closePoll(poll_key):
  # TODO: Reroute to a PATCH request to store in Redis. More RESTful.
  init_key = request.args.get('key')
  poll_data = md.getPoll(poll_key)
  if init_key != poll_data['initiator']:
    return render_template('badinitiator.html')
  else:
    # Close Poll
    md.closePoll(poll_key)
    # TODO: Notify people
    message = 'Poll \'' + poll_data['name'] + '\' closed.\n'
    results_path = '/' + poll_key + '/results'
    log_stmt = {
      'message': message,
      'links': [
        {
          'href': config.conf['DOMAIN_ROOT'] + results_path,
          'text': 'See Results'
        }
      ]
    }
    with open(config.conf['LOG_FILE'], 'a') as fh:
      fh.write(dumps(log_stmt) + '\n')
    # TODO: Delete people's info
    # TODO: Redirect to results page
    return 'Closed Poll!'

# TODO: Remove this route after emailing is implemented
@app.route('/log', methods = ['GET'])
def logDisplay():
  log_lines = []
  with open('log.txt', 'r') as fh:
    for line in fh:
      if line != None:
        line_dict = loads(line)
        log_lines.append(line_dict)
  return render_template('log.html', data = log_lines)

# TODO: Remove this route after emailing is implemented
@app.route('/clearlog', methods = ['GET'])
def clearLog():
  md.clear_redis()
  open('log.txt', 'w').close()
  return redirect(url_for('logDisplay'))

if __name__ == '__main__':
  app.run(debug = True)
  # To run publicly: app.run(host = '0.0.0.0')
