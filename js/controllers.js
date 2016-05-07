var msngrControllers = angular.module('cControllers', []);

msngrControllers.controller('LoginController', function () {
	this.credentials = {};
	this.submit = function() {
		console.log(this.credentials);
	}
});
