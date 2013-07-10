"""
BallotBox

Author: David Moench
Overview: A polling application.
"""

from flask import Flask, url_for, render_template, request
app = Flask( __name__ )

@app.route( '/', methods = ['GET', 'POST'] )
def indexPage():
  """
    The index page. 'GET' generates a form to describe a new poll.
    'POST' creates the new poll on the DB.
  """
  if request.method == 'GET':
    return render_template( 'pollcreate.html' )
  else: # POST
    result = ''
    for key in request.form:
      result += request.form[ key ]
    return result

@app.route( '/<poll_key>/<participant_key>', methods = ['GET', 'PUT'] )
def participantPollPage():
  """
    The participants' voting page. 'GET' generates the participant's ballot.
    'PUT' submits and stores their vote.
  """
  # if request.method == 'GET':
    # TODO
  # else:
    # TODO

if __name__ == '__main__':
  app.run( debug = True )
  # To run publicly: app.run( host = '0.0.0.0' )
