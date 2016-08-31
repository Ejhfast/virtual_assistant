$(document).ready(function(){
	print('hello')
	$('input[name="arg"]').blur(function() {
		if(!this.value) {
			$(this).addClass('empty_warning');
		}
	});
})