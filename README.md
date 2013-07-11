BallotBox
=========

Overview
--------
BallotBox (working title) is a polling/voting web application that prevents
fraudulent double-voting, but does not require voters to register (too much
effort). An Initiator creates a poll, specifying the options to vote for
and the emails of participants. BallotBox emails a unique ballot link to
each participant that allows them to vote only once. After the poll closes
a link to the results is emailed to everyone.

Components
----------
* [CoffeeScript](http://coffeescript.org/)
* [Python](http://www.python.org/)
* [Flask](http://flask.pocoo.org/)
* [Redis](http://redis.io/)

Installation
------------
