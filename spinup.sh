#-----------------------------------------------------------------------------#
# Startup script to activate all necessary components for dev version
# of BallotBox
#-----------------------------------------------------------------------------#
#
# Start the redis server
redis-server &
# Start coffee script autocompile
cake watch &
