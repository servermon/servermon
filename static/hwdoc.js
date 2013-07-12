function fetch_and_update(obj, url) {
  var hwdocurl = $(obj).children('a').attr('href').replace('1/','');
  $.get(url + obj.id,
  function(data) {
    var r = '';
    for (item in data.val) {
      if ( data.val[item].hasOwnProperty(data.key) ) {
        r = r + '<li><a href="' + hwdocurl + data.val[item][data.key] + '">' + data.val[item].fields.name + '</a></li>';
      } else {
        r = r + '<li><a href="' + hwdocurl + data.val[item].fields[data.key] + '">' + data.val[item].fields.name + '</a></li>';
      }
    }
    $(obj).children('ul').html(r);
  });
}

$(document).ready(function() {
  $('.toggles').on('click', function(event) {
    var toggle = $(this).data('toggle');
    event.preventDefault();
    event.stopPropagation();
    $(toggle).toggle('slow');
  });
});
