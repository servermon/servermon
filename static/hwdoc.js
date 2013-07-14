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

// A custom label formatter used by several of the plots
function labelFormatter(label, series) {
  return "<div style='font-size:8pt; text-align:center; padding:2px; color:white;'>" + label + "<br/>" + Math.round(series.percent) + "%</div>";
}

$(document).ready(function() {
  $('.toggles').on('click', function(event) {
    var toggle = $(this).data('toggle');
    event.preventDefault();
    event.stopPropagation();
    $(toggle).toggle('slow');
  });
});


$(document).ready(function() {
  $('.hwdocgraph').each(function (index) {
    var url = $(this).data('get');
    var div = $(this);
    $.get(url, function(data) {
    div.plot(data, {
      series: {
          pie: {
              show: true,
              radius: 1,
              label: {
                  show: true,
                  radius: 0.7,
                  formatter: labelFormatter,
                  threshold: 0.05
              }
          }
      },
      grid: {
	  hoverable: true,
	  clickable: true
      },
      legend: {
          show: true
      }
     });
    });
 });
});
