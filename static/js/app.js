$( function () {

	$("a.hide_url").each( function () {
		var link = $(this),
			anim_time = 500;
		link.click( function (e) {

			$.get(link.attr("href"), function (response) {
				link.parent().animate({opacity:0, height:0}, anim_time, function (){
					$(this).remove();
				});
			});

			if(e.preventDefault){
				e.preventDefault();
			}
			else {
				e.returnValue = false;
			}

		})
	})

});