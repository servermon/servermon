function fetch_and_update(obj, url) {
  var hwdocurl = $(obj).children('a').attr('href').replace('1/','');
  $.get(url + obj.id,
  function(data) {
    var r = '';
    for (item in data) {
      r = r + '<li><a href="' + hwdocurl + data[item].pk + '">' + data[item].fields.name + '</a></li>';
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
