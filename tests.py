"""
BallotBox Test Suite.

Instructions:
  Start the following processes:
    1. redis-server
    2. BallotBox's virtualenv
    3. application.py server
  Then, 'python tests.py'
"""
import redis

def runTests():
  testRedis()
  print 'All tests passed!'

def check( predicate ):
  if not predicate:
    raise Exception( 'Check failed' )

def testRedis():
  client = redis.StrictRedis( host='localhost', port=6379, db = 0 )
  client.set( 'v1', 'test value 1' )
  check( client.get('v1') == 'test value 1' )

if __name__ == '__main__':
  runTests()
