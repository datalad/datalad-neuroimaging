function submit_spec(ses) {
  var submit_button = document.getElementById('submit_spec');
  submit_button.addEventListener('click', function(e) {

      form = document.getElementById('spec_form');
      json = [];
      var rows = form.querySelectorAll('.spec_section');
      for (var i = 0, r; r = rows[i++];) {
        var json_row = {};
        attributes = r.querySelectorAll('.key');

        for (var j = 0, c; c = attributes[j++];) {
          var inputs = c.querySelectorAll('input');
          if (inputs.length == 1) {
          json_row[inputs[0].name] = inputs[0].value;
          }
          if (inputs.length == 2) {
            json_row[inputs[0].name] = {'value': inputs[0].value,
                                        'approved': inputs[1].value};
          }

        }
        json.push(json_row);
      }

      var post_data = JSON.stringify({ 'content': json});
      var xhr = new XMLHttpRequest();
      // TODO: ses can be none!
      xhr.open('POST', '/save/' + ses, true);  //TODO: what's that "true" for?
      xhr.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');
      xhr.onload = function() {
        if (this.status === 200) {
          console.log(this.responseText);
          window.location = this.responseText;
        } else {
          console.log(post_data);
          alert("That's... well, it's not supposed to happen. :'("
          + "\n" + this.status);
        }
      };

      xhr.send(post_data);
  });
}
