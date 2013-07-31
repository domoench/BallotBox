###
  A generic module to handle conversion of a HTML form element to a JSON object
###
define 'serialize', [ 'jquery', 'underscore' ], ( $, _ ) ->
  serialize =
    elements_of_interest : [ 'input', 'select', 'textarea' ] #TODO: This is selecting the input:submit element

    getFormData : ( form_selector ) ->
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
      elements = $( form_selector ).children()
      # Get object of all input elements
      inputs = _.filter elements, ( element ) =>
        _.contains @elements_of_interest, $( element ).prop 'localName'
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
        [ (@getInputKey $elem), (@getInputValue $elem) ]
      other_pair_obj = _.object other_pair_list
      choices_obj =
        choices: _.map choices, ( elem ) ->
          $( elem ).val()
      part_string = $( participants[0] ).val()
      part_list = part_string.split /[\s\n,]+/
      console.log 'part_list', part_list
      part_obj =
        participants: part_list
      result_obj = _.extend choices_obj, part_obj, other_pair_obj

    commaStringToList: ( raw_form_object ) ->
      ###
        Package an object output by getFormData into the format expected by
        the BalltoBox Flask backend.

        @param {Object} raw_form_obj An object of form input data
        @return {Object} packaged_obj An object of form input data formatted
                                         for the BallotBox poll creation method
                                         on the backend.
      ###
      packaged_obj = _.clone( raw_form_object )
      processed_participants = []


    # TODO: Is it even worth having getInputKey and getInputValue as methods?
    getInputKey : ( $elem ) ->
      ###
        Return the name key of a jQuery input element.

        @param {jQuery} $elem
        @return {String}
      ###
      $elem.attr 'name'

    getInputValue : ( $elem ) ->
      ###
        Return the value attribute of a jQuery input element.

        @param {jQuery} $elem
        @return {String}
      ###
      $elem.val()
