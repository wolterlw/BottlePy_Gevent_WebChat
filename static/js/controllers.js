var msngrControllers = angular.module('cControllers', []);

msngrControllers.controller('LoginController', function () {
	//have no idea where it supposed to be
    $("#menu-toggle").fadeOut(0);
});
msngrControllers.controller('SignInController', ['LoginService', function(LoginService) {
	this.credentials = {};
	this.submit = function() {
		console.log("SignInController: this.credentials=", this.credentials);
		LoginService.signIn(this.credentials);
	}
	this.toggleLogin = function() {
        $(".form-signin").remove();
        $(".form-signup").fadeIn();
	}
}]);
msngrControllers.controller('SignUpController', ['LoginService', function(LoginService) {
	this.newUser = {};
	this.submit = function() {
		//cut our json, because of the backend
		delete this.newUser.email
		console.log("SignUpController: this.newUser=", this.newUser);
		LoginService.signUp(this.newUser);
	}
}]);

msngrControllers.controller('MessagesController', ['$http', 'AuthService', function($http, AuthService) {
	//have no idea where it supposed to be
	$("#menu-toggle").fadeIn(0);

	var self = this;
	this.buddyList = {};
	$http.get("/users/"+AuthService.getId())
		.success(function (data) {
			self.buddyList = data;
			console.log("MessagesController, success: self.buddyList=", self.buddyList);
		})
		.error(function(data) {
			//handle error
			console.log("MessagesController, error: data=", data);
		});
}]);