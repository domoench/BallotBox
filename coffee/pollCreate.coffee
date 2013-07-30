define 'pollCreate', [ 'jquery', 'underscore', 'serialize' ], ( $, _, serialize ) ->
  console.log 'pollCreate.coffee has compiled and is running!'
  $('form').submit ( event ) ->
    serialize.getFormData( $(this).find 'fieldset' )
    false # Prevent default submit
  null
