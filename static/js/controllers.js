var msngrControllers = angular.module('cControllers', []);

msngrControllers.controller('LoginController', function () {
	//have no idea where it supposed to be
    $("#menu-toggle").fadeOut(0);
});
msngrControllers.controller('SignInController', function($http) {
	this.credentials = {};
	this.submit = function() {
		console.log(this.credentials);
		//use service for logging
		$http.post('/login', this.credentials)
            .success(function (data) {
               console.log("success: ", data);
            })
            .error(function (data) {
               console.log("error: ", data);
            });
	}
	this.toggleLogin = function() {
        $(".form-signin").remove();
        $(".form-signup").fadeIn();
	}
});
msngrControllers.controller('SignUpController', function() {
	this.newUser = {};
	this.submit = function() {
		console.log(this.newUser);
		//use service for logging 
	}
});
