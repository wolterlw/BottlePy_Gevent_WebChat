var msngrControllers = angular.module('cControllers', []);

msngrControllers.controller('LoginController', function () {
	//have no idea where it supposed to be
    $("#menu-toggle").fadeOut(0);

	this.credentials = {};
	this.submit = function() {
		console.log(this.credentials);
		//use service for logging 
	}
	this.toggleLogin = function() {
        $(".form-signin").remove();
        $(".form-signup").fadeIn();
	}
});
