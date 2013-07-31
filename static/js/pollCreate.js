// Generated by CoffeeScript 1.6.2
(function() {
  define('pollCreate', ['jquery', 'underscore', 'serialize'], function($, _, serialize) {
    $('#add-button').click(function(event) {
      var index, last_choice, new_index;

      last_choice = $('fieldset .choice').last();
      index = last_choice.attr('index');
      new_index = (parseInt(index)) + 1;
      last_choice.after('<br><input name=\'choice[' + new_index + ']\' class=\'choice\' index=\'' + new_index + '\'>');
      console.log(last_choice);
      return null;
    });
    $('form').submit(function(event) {
      var form_obj;

      form_obj = serialize.getFormData($(this).find('fieldset'));
      console.log(form_obj);
      return false;
    });
    return null;
  });

}).call(this);
