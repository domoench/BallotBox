###
  A generic module to handle conversion of a HTML form element to a JSON object
###
define 'serialize', [ 'jquery', 'underscore' ], ( $, _ ) ->
  serialize =
    elements_of_interest : [ 'input', 'select' ]
    grab : ( form_selector ) ->
      ###
        @param {String} form_selector The jQuery selector string for the form
                                      to be serialized.
      ###
      elements = $( form_selector ).children()
      inputs = _.filter elements, ( element ) =>
        _.contains @elements_of_interest, $( element ).prop 'localName'
      console.log inputs
      null
