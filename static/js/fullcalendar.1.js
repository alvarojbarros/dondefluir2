function getCalendar(user_id) {

	var today = new Date();
	var dd = today.getDate();
	var mm = today.getMonth()+1; //January is 0!
	var yyyy = today.getFullYear();
	if(dd<10) {dd='0'+dd}
	if(mm<10) {mm='0'+mm}
	today = yyyy+'-'+mm+'-'+dd;

    $('#calendar').fullCalendar({
		header: {
			left: 'prev,next today',
			center: 'title',
			right: 'month,agendaWeek,agendaDay'
		},
		locale: 'es',
		height: 500,
		defaultDate: today,
		editable: true,
		eventLimit: true, // allow "more" link when too many events
		events: {
			url: 'calendar_data',
			data: {UserId: user_id},
			error: function() {
			$('#script-warning').show();
			}
		},
		loading: function(bool) {
			$('#loading').toggle(bool);
		},

		eventRender: function(event, element) {
		},

		eventClick: function(event) {
			if (event.url) {
				window.open(event.url);
				return false;
			}
			if (event.onclick) {
				console.log(event.onclick)
				var onclick_function = new Function(event.onclick);
				onclick_function();
				return false;
			}
		}
    });

}

