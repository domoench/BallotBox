define 'pollCreate', [ 'jquery', 'underscore' ], ( $, _ ) ->
  ###
    JQUERY SETUP
  ###
  # Add button dynamically adds choice input fields
  $( '#add-button' ).click ( event ) ->
    last_choice = $( 'fieldset .choice' ).last()
    index = last_choice.attr 'index'
    new_index = ( parseInt index ) + 1
    last_choice.after '<br><input name=\'choice[' + new_index +
                      ']\' class=\'choice\' index=\'' + new_index + '\'>'
    console.log last_choice
    null

  # On submit, parse form data into a javascript Object and PUT to Flask
  $( 'form' ).submit ( event ) ->
    form_obj = getFormData( $(this).find 'fieldset' )
    ajax_settings =
      type: 'PUT'
      url: ''
      contentType: 'application/json'
      data: JSON.stringify form_obj
    promise = $.ajax ajax_settings
    promise.done ( data ) ->
      $( '#content' ).html '<p>Form Created</p>'
    promise.fail ( jqXHR, textStatus, errorThrown ) ->
      throw new Error( errorThrown )
    false # Prevent default submit

  ###
    HELPER FUNCTIONS
  ###
  getFormData = ( form_selector ) ->
    ###
      Serialize the input from an HTML form into a javascript object. Inputs
      with the class 'choice' are packaged together as a list and assigned
      to the 'choices' property of the result object. All other properties
      derive their keys and values directly from the form elements' name and
      value.

      @param {String} form_selector The jQuery selector string for the form
                                    fieldset to be serialized.
      @return {Object} result_obj A serialized object representation of the
                                  form data
    ###
    elements_of_interest = [ 'input', 'select', 'textarea' ]
    elements = $( form_selector ).children()
    # Get object of all input elements
    inputs = _.filter elements, ( element ) =>
      _.contains elements_of_interest, $( element ).prop 'localName'
    console.log 'inputs:', inputs
    choices = _.filter inputs, ( input ) ->
      ( $(input).prop 'className' ) is 'choice'
    # Get participants input
    participants = _.filter inputs, ( input ) ->
      ( $(input).prop 'localName' ) is 'textarea'
    # Remove the choice and participant elements from inputs
    other_inputs = _.difference( inputs, choices, participants )
    # Serialize inputs
    other_pair_list = _.map other_inputs, ( elem ) =>
      $elem = $( elem )
      [ ($elem.attr 'name'), ($elem.val()) ]
    other_pair_obj = _.object other_pair_list
    choices_obj =
      choices: _.map choices, ( elem ) ->
        $( elem ).val()
    part_string = $( participants[0] ).val()
    part_list = part_string.split /[\s\n,]+/
    part_obj =
      participants: part_list
    result_obj = _.extend choices_obj, part_obj, other_pair_obj

  null
