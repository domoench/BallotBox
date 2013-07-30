'use strict'

# Setup RequireJS
require.config(
  baseUrl: '/static/js'
  paths:
    'jquery'     : 'components/jquery/jquery.min'
    'underscore' : 'components/underscore/underscore-min'
)

require [ 'jquery', 'underscore' ], ( $, _ ) ->
  # TODO: Any additional setup code here
  console.log 'requireConfig.coffee has been run. jQuery and Underscore have been required.'
