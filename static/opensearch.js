function opensearch(request, response, url) {
	$.ajax({
	    url: url,
	    dataType: "json",
	    data: {
		'action': "opensearch",
		'format': "json",
		'q': request.term
	    },
	    success: function(data) {
		response(data[1]);
	    }
	});
}
