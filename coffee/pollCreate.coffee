define 'pollCreate', [ 'jquery', 'underscore', 'serialize' ], ( $, _, serialize ) ->
  # Add button dynamically adds choice input fields
  $( '#add-button' ).click ( event ) ->
    last_choice = $( 'fieldset .choice' ).last()
    index = last_choice.attr 'index'
    new_index = ( parseInt index ) + 1
    last_choice.after '<br><input name=\'choice[' + new_index +
                      ']\' class=\'choice\' index=\'' + new_index + '\'>'
    console.log last_choice
    null

  # On submit, parse form data into a javascript Object
  $('form').submit ( event ) ->
    form_obj = serialize.getFormData( $(this).find 'fieldset' )
    console.log form_obj
    false # Prevent default submit
  null
