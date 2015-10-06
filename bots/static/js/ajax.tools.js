function ajaxFormSuccess(json, statusText, form)
{
	rsZone = $("#"+form.attr('id')+ " .result-ajax");
	if(json.success)
	{
		rsZone.addClass("result-ajax-success");
		rsZone.removeClass("result-ajax-error");
		rsZone.html(json.msg)
		
	 //TODO reload the grid and the whole page after few seconds in order to reflect the transaction
	}
	else
	{
		rsZone.removeClass("result-ajax-success");
		rsZone.addClass("result-ajax-error");
		rsZone.html(json.msg)	
	}
}

function ajaxFormError(responseText, statusText, msg)
{
	rsZone = $($(this).attr('target'));
	rsZone.html("Error charging: " + msg)
	rsZone.removeClass("result-ajax-success");
	rsZone.addClass("result-ajax-error");
}
