"""
BallotBox

Author: David Moench
Overview: A polling application.
"""

from flask import Flask, url_for
app = Flask( __name__ )

@app.route( '/', methods = ['GET'] )
def indexPage():
  """
    The index page. Consists of a form to generate a new poll.
  """
  return '<h1>Create a new poll</h1>'

@app.route( '/polls/<poll_key>/<participant_key>', methods = ['GET', 'PUT'] )
def participantPollPage():
  """
    The participants' voting page. 'GET' generates the participant's ballot.
    'PUT' submits and stores their vote.
  """
  if request.method == 'GET':
    # TODO
  else:
    # TODO

if __name__ == '__main__':
  app.run( debug = True )
  # To run publicly: app.run( host = '0.0.0.0' )
