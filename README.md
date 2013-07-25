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

Components
----------
* [CoffeeScript](http://coffeescript.org/)
* [Python](http://www.python.org/)
* [Flask](http://flask.pocoo.org/)
* [Redis](http://redis.io/)

Installation
------------
In your virtualenv you must have the following installed:
* [Flask](http://flask.pocoo.org/docs/installation/)
* [redis-py](https://pypi.python.org/pypi/redis/)

Create the following UNIX environment variables to pull in credentials:

1. MANDRILL_USER: Mandrill email service username
2. MANDRILL_PASS: Mandrill email service password
