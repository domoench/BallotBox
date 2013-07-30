###
  A generic module to handle conversion of a HTML form element to a JSON object
###
define 'serialize', [ 'jquery', 'underscore' ], ( $, _ ) ->
  serialize =
    elements_of_interest : [ 'input', 'select' ] #TODO: This is selecting the input:submit element

    getFormData : ( form_selector ) ->
      ###
        @param {String} form_selector The jQuery selector string for the form
                                      to be serialized.
      ###
      elements = $( form_selector ).children()
      inputs = _.filter elements, ( element ) =>
        _.contains @elements_of_interest, $( element ).prop 'localName'
      pair_list = _.map inputs, ( elem ) =>
        $elem = $( elem )
        [ (@getInputKey $elem), (@getInputValue $elem) ]
      result_obj = _.object pair_list
      console.log result_obj
      null

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
