define 'pollAdmin', [ 'jquery', 'underscore' ], ( $, _ ) ->
  ###
    JQUERY SETUP
  ###
  # Add Participants Form. On submit, parse form data into a Javascript
  # list and POST to Flask
  $( 'form#admin-add' ).submit ( event ) ->
    part_list = getParticipantForm ( $(this).find 'fieldset' )
    console.log part_list
    ajax_settings =
      type: 'POST'
      url: ''
      contentType: 'application/json'
      data: JSON.stringify part_list
      # promise = $.ajax ajax_settings
    # TODO promise.done
    false # Prevent default submit

  ###
    HELPER FUNCTIONS
  ###
  getParticipantForm = ( form_selector ) ->
    ###
      TODO
    ###
    part_textarea = $( form_selector ).find('textarea')
    part_string = $( part_textarea ).val()
    part_list = part_string.split /[\s\n,]+/

  null
