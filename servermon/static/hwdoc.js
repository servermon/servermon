function BuildNavs(obj) {
  $.get($(obj).data("get"),
  function(data) {
    var r = "";
    for (var item in data) {
        r = r + "<li><a href='" + data[item].url + "'>" + data[item].name + "</a></li>";
      }
    $(obj).next().html(r);
    });
}

// A custom label formatter used by several of the plots
function labelFormatter(label, series) {
  return "<div style='font-size:8pt; text-align:center; padding:2px; color:white;'>" + label + "<br/>" + Math.round(series.percent) + "%</div>";
}

$(document).ready(function() {
  var url = $("input#q").data("get");
  $("input#q").typeahead({
    minLength: 2,
    source(query, process) {
      $.get(url, { q: query, limit: 8 }, function(data) {
      process(data[1]);
    });
    },
    updater(item) {
      this.$element.context.parentNode.submit();
      return item;
    },
    sorter(items) {
      items.unshift(this.query);
      return items;
    }
  });
});

$(document).ready(function() {
  $(".sortable").tablesorter();
});

$(document).ready(function() {
  $(".dist-upgrade").tooltip();
});

$(document).ready(function() {
  $(".hwdocfetchable").on("click", function(event) {
      event.preventDefault();
      event.stopPropagation();
    }).on("mouseenter", function(event) {
      BuildNavs(this);
    });
});

$(document).ready(function() {
  $(".toggles").on('click', function(event) {
    var toggle = $(this).data("toggle");
    event.preventDefault();
    event.stopPropagation();
    $(toggle).toggle("slow");
  });
});

$(document).ready(function() {
  $(".hwdocgraph").each(function (index) {
    var url = $(this).data("get");
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
