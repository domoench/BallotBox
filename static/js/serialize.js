// Generated by CoffeeScript 1.6.2
/*
  A generic module to handle conversion of a HTML form element to a JSON object
*/


(function() {
  define('serialize', ['jquery', 'underscore'], function($, _) {
    var serialize;

    return serialize = {
      elements_of_interest: ['input', 'select'],
      getFormData: function(form_selector) {
        /*
          @param {String} form_selector The jQuery selector string for the form
                                        to be serialized.
        */

        var elements, inputs, pair_list, result_obj,
          _this = this;

        elements = $(form_selector).children();
        inputs = _.filter(elements, function(element) {
          return _.contains(_this.elements_of_interest, $(element).prop('localName'));
        });
        pair_list = _.map(inputs, function(elem) {
          var $elem;

          $elem = $(elem);
          return [_this.getInputKey($elem), _this.getInputValue($elem)];
        });
        result_obj = _.object(pair_list);
        console.log(result_obj);
        return null;
      },
      getInputKey: function($elem) {
        /*
          Return the name key of a jQuery input element.
        
          @param {jQuery} $elem
          @return {String}
        */
        return $elem.attr('name');
      },
      getInputValue: function($elem) {
        /*
          Return the value attribute of a jQuery input element.
        
          @param {jQuery} $elem
          @return {String}
        */
        return $elem.val();
      }
    };
  });

}).call(this);
