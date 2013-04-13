var heart = "data:image/png;base64,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";

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
	});

	function like_keyword(e) {
		var keyword = $(this),
			params = {keyword: keyword.text(), bad: 0};
		$.post('/keyword', params, function (response) {
			// console.log("Hello");
			var heart_div = $("<div><img src='"+heart+"'></div>").appendTo($("body"));
			heart_div.css({
				position:"absolute",
				opacity:0.9
			});
			heart_div.offset({
				left:e.pageX-25,
				top:e.pageY-15
			});
			heart_div.animate({opacity:0}, 700, function () {
				$(this).remove()
			});
		});
	}

	$(".entry-content").each( function () {
		var keywordable_elements = [],
			split_text = $(this).text().split(' ');
		// console.log(split_text);
		$.each(split_text, function () {
			keywordable_elements.push("<span class='hoverable_keyword'>"+this+"</span>");
		});
		// $(this).html('');
		// var paragraph = $(this);
		// $.each(keywordable_elements, function () {
			// paragraph.append(" "+this);
		// });

		$(this).html(keywordable_elements.join(" "));
		$(this).find("span").each( function () {
			$(this).click( function (e) {
				like_keyword(e);
			});
		});
	});


	$(".keyword").each( function () {

		$(this).click( function (e) {
			like_keyword(e);
		});
		
	});

});