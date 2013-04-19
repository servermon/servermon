function fetch_and_update(obj, url) {
  $.get(url + obj.id,
  function(data) {
    var r = '';
    for (item in data) {
      r = r + '<li><a href="#">' + data[item].fields.name + '</a></li>';
    }
    $(obj).children('ul').html(r);
  });
}
