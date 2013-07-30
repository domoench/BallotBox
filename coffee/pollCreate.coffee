define 'pollCreate', [ 'jquery', 'underscore', 'serialize' ], ( $, _, serialize ) ->
  console.log 'pollCreate.coffee has compiled and is running!'
  serialize.getFormData('form fieldset')
  null
