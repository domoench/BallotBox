define 'pollAdmin', [ 'jquery', 'underscore' ], ( $, _ ) ->
  ###
    JQUERY SETUP
  ###
  # Get data stored in the #json-data div
  json_data_string = $( '#json-data' ).html()
  json_data = JSON.parse json_data_string
  poll_key = json_data['poll_key']
  init_key = json_data['init_key']

  # Add Participants Form. On submit, parse form data into a Javascript
  # list and POST to Flask
  $( 'form#admin-add' ).submit ( event ) ->
    part_list = getParticipantForm ( $(this).find 'fieldset' )
    ajax_settings =
      type: 'POST'
      url: '/' + poll_key + '/participants?key=' + init_key
      contentType: 'application/json'
      data: JSON.stringify part_list
    promise = $.ajax ajax_settings
    promise.done ( data ) ->
      $( '#content' ).prepend '<p id=\'status-msg\'>Participants Added</p>' #TODO: Make closable
    promise.fail ( jqXHR, textStatus, errorThrown ) ->
      throw new Error( errorThrown )
    false # Prevent default submit

  # Close Poll Form
  $( 'form#admin-close' ).submit ( event ) ->
    ajax_settings =
      type: 'PUT'
      url: '/' + poll_key + '/status?key=' + init_key
      contentType: 'text/plain'
      data: 'closed'
    promise = $.ajax ajax_settings
    promise.done ( data ) ->
      $( '#content' ).prepend '<p id=\'status-msg\'>Poll Closed</p>' #TODO: Make closable
    promise.fail ( jqXHR, textStatus, errorThrown ) ->
      throw new Error( errorThrown )
    false

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
