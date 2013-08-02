"""
    Handles interaction between BallotBox Flask app and Redis DB

    TODO: Find where you can pass in data dicts instead of keys to
                reduce trips to the DB
"""
import redis
import datetime
import helpers
from json import dumps, loads
import config # TODO: Remove this when temporary log file notification is no longer used

class Model:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client = redis.StrictRedis(host = self.host, port = self.port, db = 0)

    def create_poll(self, poll_data_raw):
        """
        Create a new poll record on the DB. Takes a dictionary of poll data,
        generates keys for the poll, initiator, and participants, and stores it
        to the DB.

        Args:
            poll_data_raw: a python dictionary of validated, unprocessed poll data of
                the following form:
                {
                    'name': 'Favorite Color',
                    'choices': ['Red', 'Blue', 'Green', 'Teal'],
                    'close': datetime.datetime(2014, 7, 11, 4, 0).isoformat(),
                    'participants': ['alouie@gmail.com', 'lluna@gmail.com'],
                    'type': 'plurality',
                    'initiator': 'david.moench@arc90.com'
                }

        Returns:
            The created poll's key string. For example:
                'poll_0c9a1081760990bcc89ca94bb6bdd5710328f3ef'
        """
        now = datetime.datetime.utcnow()
        close = datetime.datetime.strptime(poll_data_raw['close'],
                                           '%Y-%m-%dT%H:%M:%S')
        ongoing = close - now > datetime.timedelta(minutes = 0)
        init_key = helpers.generateKeyString(poll_data_raw['initiator'],
                                             now.isoformat(), 'init_')
        part_map = {}
        for email in poll_data_raw['participants']:
            part_key = helpers.generateKeyString(email, now.isoformat(),
                                                 'part_')
            part_map[part_key] = email
        poll_data_processed = {
            'name': poll_data_raw['name'],
            'choices': filter(bool, poll_data_raw['choices']),
            'ongoing': ongoing,
            'close': poll_data_raw['close'],
            'type': poll_data_raw['type'],
            'initiator': init_key,
            'participants': part_map
        }
        poll_key = helpers.generateKeyString(poll_data_raw['name'],
                                             now.isoformat(), 'poll_')
        self.client.set(poll_key, dumps(poll_data_processed))

        # Create initiator's record
        init_data = {
            'email': poll_data_raw['initiator'],
            'poll': poll_key
        }
        self.set_initiator(init_key, init_data)

        # Create participants' records
        for part_key in part_map:
            part_data_raw = {
                'email': part_map[part_key],
                'poll': poll_key,
                'voted': False,
                'choice': None
            }
            self.set_participant(part_key, part_data_raw)

        return poll_key

    def set_initiator(self, init_key, init_data_raw):
        """
        Create a new, or set an existing, Initiator record on the DB.

        Args:
            init_key: The initiator's key string. For Example:
                init_4dc6297e78836e8a5c48b0deb3b7cf3ace70b300
            init_data_raw:  a python dictionary of validated, unprocessed
                initiator data of the following form:
                {
                    'email': 'david.moench@arc90.com',
                    'poll': 'poll_0c9a1081760990bcc89ca94bb6bdd5710328f3ef'
                }

        Returns:
            The initiator's key string.
        """
        self.client.set(init_key, dumps(init_data_raw))
        return init_key

    def set_participant(self, part_key, part_data_raw):
        """
        Create a new Participant record on the DB.

        Args:
            part_key: The participant's key string. For Example:
                'part_247fd90ba860b79ef41e0770638c69bac98cbd94'
            part_data_raw: a python dictionary of validated, unprocessed
                participant data of the following form:
                {
                    'email': 'alouie@gmail.com',
                    'poll': 'poll_0c9a1081760990bcc89ca94bb6bdd5710328f3ef',
                    'voted': True,
                    'choice': 1
                }
                Note: If 'voted' is False, 'choice' should be None

        Returns:
            The participant's key string.
        """
        self.client.set(part_key, dumps(part_data_raw))
        return part_key

    def get_poll(self, poll_key):
        """
        Get and JSON decode a poll record.

        Args:
            poll_key: The poll's key string.

        Returns:
            A python dictionary of the record, or None if no record found.
        """
        if poll_key[:5] != 'poll_':
            raise Exception('Incorrect key passed to get_poll(): ' + poll_key)
        poll_data = self.client.get(poll_key)
        if poll_data is None:
            return None
        else:
            return loads(poll_data)

    def get_participant(self, part_key):
        """
        Get and JSON decode a participant record.

        Args:
            part_key: The participant's key string.

        Returns:
            A python dictionary of the record, or None if no record found.
        """
        if part_key[:5] != 'part_':
            raise Exception('Incorrect key passed to getPartiticpant(): ' + part_key)
        part_data = self.client.get(part_key)
        if part_data is None:
            return None
        else:
            return loads(part_data)

    def get_initiator(self, init_key):
        """
        Get and JSON decode a initiator record.

        Args:
            init_key: The initiator's key string.

        Returns:
            A python dictionary of the record, or None if no record found.
        """
        if init_key[:5] != 'init_':
            raise Exception('Incorrect key passed to model.get_initiator(): ' +
                            init_key)
        init_data = self.client.get(init_key)
        if init_data is None:
            return None
        else:
            return loads(init_data)

    def vote(self, part_key, choice):
        """
        Set the participant record's 'choice' attribute and set its 'voted'
        attribute to True.

        Args:
            part_key: The participant's key string.
            choice: An integer offset into the parent poll's 'choices' list

        Return:
            The participant data dictionary.
        """
        part_data = self.get_participant(part_key)
        poll_key = part_data['poll']
        poll_data = self.get_poll(poll_key)
        num_choices = len(poll_data['choices'])
        if(choice not in range(num_choices)):
            raise Exception('Invalid choice value ' + choice +
                            ' provided to model.vote()')
        part_data['choice'] = choice
        part_data['voted'] = True
        self.set_participant(part_key, part_data)
        # TODO: Remove the following notification after the demo
        message = ('Participant ' + part_data['email'] + ' voted for ' +
                    poll_data['choices'][part_data['choice']] + '.')
        log_stmt = {'message': message, 'links': None}
        with open(config.conf['LOG_FILE'], 'a') as fh:
            fh.write(dumps(log_stmt) + '\n')
        return part_data

    def add_poll_participants(self, poll_key, new_participants):
        """
        Add new participants to an ongoing poll.

        Args:
            poll_key: The poll's key string.
            new_participants: A List of well-formed participant email strings.

        Returns:
            A map of key:email pairs for newly added participants. For example:
            {
                'part_247fd90ba860b79ef41e0770638c69bac98cbd94': 'alouie3@gmail.com',
                'part_0c9a1081760990bcc89ca94bb6bdd5710328f3ef': 'lluna@gmail.com'
            }
        """
        poll_data = self.get_poll(poll_key)
        participants = poll_data['participants']
        part_emails = participants.values()
        now_str = datetime.datetime.utcnow().isoformat()

        new_part_map = {}
        for email in new_participants:
            if email not in part_emails: # No duplicate emails
                # Add new participant key to the Poll
                new_part_key = helpers.generateKeyString(email, now_str,
                                                        'part_')
                participants[new_part_key] = email
                self.client.set(poll_key, dumps(poll_data))
                # Create new participant record
                new_part_data_raw = {
                    'email':    email,
                    'poll': poll_key,
                    'voted': False,
                    'choice': None
                }
                self.set_participant(new_part_key, new_part_data_raw)
                new_part_map[new_part_key] = email
        return new_part_map

    def check_poll_ongoing(self, poll_key):
        """
        Checks if the poll is still ongoing (meaning there is still time left).

        Args:
            poll_key: The poll's key string.

        Returns:
            Boolean. True if there is still time left in the poll. False
            otherwise.
        """
        poll_data = self.get_poll(poll_key)
        if not poll_data['ongoing']:
            return False
        now = datetime.datetime.utcnow()
        close = datetime.datetime.strptime(poll_data['close'],
                                          '%Y-%m-%dT%H:%M:%S')
        time_remains = close - now > datetime.timedelta(minutes = 0)
        if not time_remains:
            return False
        else:
            return True

    def close_poll(self, poll_key):
        """
        Sets the poll's 'ongoing' field to False

        Args:
            poll_key: The poll's key string.
        """
        poll_data = self.get_poll(poll_key)
        poll_data['ongoing'] = False
        self.client.set(poll_key, dumps(poll_data))
        # TODO: Notify the participants and send them the results: notify.emailResults()

    def get_all_votes(self, poll_key):
        """
        Returns a list of all participants' choices.

        Args:
            poll_key: The poll's key string.

        Returns:
            A list where each element is one participant's integer choice
        """
        poll_data = self.get_poll(poll_key)
        part_keys = poll_data['participants']
        results = []
        for part_key in part_keys:
            part_choice = self.get_participant(part_key)['choice']
            results.append(part_choice)
        return results

    def delete_poll_people(self, poll_data):
        """
        Deletes the Initiator's and all Participants' DB records for the given
        poll.

        Args:
            poll_data: The poll's data dictionary.
        """
        # Delete Initator and Participant data
        self.delete_person(poll_data['initiator'])
        for part_key in poll_data['participants'].keys():
            self.delete_person(part_key)

    def delete_person(self, key):
        """
        Delete a participant or initiator record.

        Args:
            key: The particpant or initator key string
        """
        if key[:5] not in ['part_', 'init_']:
            raise Exception('model.delete_person() can only be performed on a' +
                                            'participant or initiator record.')
        # TODO: Delete this notification after testing is complete
        if key[:5] == 'part_':
            message = ('Participant ' + self.get_participant(key)['email'] +
                      ' deleted.')
        else:
            message = ('Initiator ' + self.get_initiator(key)['email'] +
                      ' deleted.')
        log_stmt = {'message': message, 'links': None}
        with open('log.txt', 'a') as fh:
            fh.write(dumps(log_stmt) + '\n')
        # Delete the DB record
        self.client.delete(key)

    def get_participant_vote_links(self, participants, poll_key):
        """
        Gets a list of participant email/vote-link pairs.

        Args:
            poll_key: The key string for the poll to which the participants belong.
            participants: A map of participant keys to emails. For example:
                {
                    'part_247fd90ba860b79ef41e0770638c69bac98cbd94': 'alouie3@gmail.com',
                    'part_0c9a1081760990bcc89ca94bb6bdd5710328f3ef': 'lluna@gmail.com'
                }

        Returns:
            A list of participant email/vote-link pair dictionaries. For example:
            [
                {
                    'email': 'alouie@gmail.com',
                    'vote_link': '/poll_0c9a1081760990bcc89ca94bb6bdd5710328f3ef/part_247fd90ba860b79ef41e0770638c69bac98cbd94
                },
                {
                    'email': 'lluna@gmail.com',
                    'vote_link': '/poll_0c9a1081760990bcc89ca94bb6bdd5710328f3ef/part_9b55ce38e1074928830b37bda5ddf325ac70a3d7
                }
            ]
        """
        result = []
        for part_key in participants.keys():
            participant_pair = {
                'email': participants[part_key],
                'vote_link': '/' + poll_key + '/' + part_key
            }
            result.append(participant_pair)
        return result

    def get_poll_progress(self, poll_key):
        """
        Return a tuple of the number of people who have voted and the number of
        poll participants

        Args:
            poll_key: The poll's key string.

        Returns:
            A tuple of integers of the the following form:
            (num_participants_voted, num_particpants)
        """
        poll_data = self.get_poll(poll_key)
        part_keys = poll_data['participants'].keys()
        num_participants = len(part_keys)
        num_voted = 0
        for part_key in part_keys:
            part_data = self.get_participant(part_key)
            if part_data['voted']:
                num_voted += 1
        return (num_voted, num_participants)

    def clear_redis(self):
        for key in self.client.keys('*'):
            self.client.delete(key)
