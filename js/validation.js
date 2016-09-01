function validateInput() {
	$('input[name="arg"]').each(function() {
		if (!$(this).val()) {
			$(this).addClass('empty_warning');		
		} else {
			$(this).removeClass('empty_warning');
		}
	})
}

function removeHighlight() {
	$('.command').each(function() {
		$(this).removeClass('highlight');
		$('#no_command').removeClass('highlight');
	})	
}

function chooseCommand(cmd) {
	removeHighlight();
	cmd.addClass('highlight');

	// get args
}

function findCommand() {
	removeHighlight();
	$('#no_command').addClass('highlight');
	
	// add / append input box inside div

}

function test_func(data) {
    console.log(data);
}

$(document).ready(function() {
	display_data = $('#data').data();
	console.log(display_data);

	$('input[name="args_submit"]').click(function() {
		validateInput();
	})

	$('.command').click(function() {
		chooseCommand($(this));
	})

	$('#no_command').click(function() {
		findCommand();
	})

})