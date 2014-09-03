BallotBox
=========

Overview
--------
BallotBox is a web application for conducting polls. It is convenient and
non-invasive because participants don't need to create user accounts, and it
prevents voter fraud.

An Initiator creates a poll, specifying the options to vote for
and the emails of participants. BallotBox emails a unique secret ballot link
to each participant that allows them to vote. After the poll closes a link to
the results is emailed to everyone and their email addresses are erased from
BallotBox's memory.

This used to be deployed on Heroku. Hopefully someday I'll get around to 
re-deploying it on my own server. For now it sleeps.

Components
----------
* [Python](http://www.python.org/)
* [Flask](http://flask.pocoo.org/)
* [Redis](http://redis.io/)
* [CoffeeScript](http://coffeescript.org/)
* [RequireJS](http://requirejs.org)

Configuration
-----------
Create a file called config.json and follow the template shown in
config.json.template, filling in the actual values.

In your virtualenv you must have the following installed:
* [Flask](http://flask.pocoo.org/docs/installation/)
* [redis-py](https://pypi.python.org/pypi/redis/)
* [mandrill] (https://mandrillapp.com/api/docs/index.python.html)

Development Notes
-----------------
Things to spin up:
* virtualenv: `. venv/bin/activate`
* Flask App: `python application.py`
* redis server: `redis-server`
* CoffeeScript auto compile: `cake watch`
