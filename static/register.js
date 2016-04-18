$(document).ready(
	function() {
    if (!window.console) window.console = {}; //checking if the console is here (not there in mobile browsers)
    if (!window.console.log) window.console.log = function(){}; //else creating empty lists and function to do nothing 

    $("#registerform").live("submit", 
    	function() {
		newRegister($(this));
		return false;
    	});

    $("#registerform").live("keypress", function(e) {
	if (e.keyCode == 13) {
	    newRegister($(this));
	    return false;
	}
    });
});

function newRegister(form) {
    var r_info = form.formToDict();

    var disabled = form.find("button[type=submit]");
    disabled.disable();
    //disable submit button
    callback_NM = function(response){
    	if (response,id == 0){
    		alert("something went wrong");
    	}else{
            console.log(response.id)
        }
    }
    $.postJSON("/a/register/new", r_info, callback_NM);
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

jQuery.postJSON = function(url, args, callback) {
    $.ajax({url: url, data: $.param(args), dataType: "text", type: "POST",
	    success: callback(response);
    }, error: function(response) {
	console.log("ERROR:", response)
    }});
};

jQuery.fn.formToDict = function() {
    var fields = this.serializeArray();
    var json = {}
    for (var i = 0; i < fields.length; i++) {
	json[fields[i].name] = fields[i].value;
    }
    if (json.next) delete json.next;
    return json;
};

jQuery.fn.disable = function() {
    this.enable(false);
    return this;
};

jQuery.fn.enable = function(opt_enable) {
    if (arguments.length && !opt_enable) {
        this.attr("disabled", "disabled");
    } else {
        this.removeAttr("disabled");
    }
    return this;
};