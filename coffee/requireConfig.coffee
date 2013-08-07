'use strict'

# Setup RequireJS
require.config(
  baseUrl: '/static/js'
  paths:
    'jquery'     : 'components/jquery/jquery.min',
    'jquery.validate': 'components/jquery/jquery.validate',
    'underscore' : 'components/underscore/underscore-min'
  shim:
    'jquery' :
        deps: ['require']
        exports: '$'
    'jquery.validate' :
        deps: ['jquery']
)

require [ 'jquery', 'jquery.validate', 'underscore' ], ( $, jq_validate, _ ) ->
  # TODO: Any additional setup code here
