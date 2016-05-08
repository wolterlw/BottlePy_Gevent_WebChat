var msngrServices = angular.module('cServices', []);

msngrServices.factory('LoginService', ['$http', function($http) {
	var obj = {};
	obj.signIn = function(credentials) {
		$http.post('/login', credentials)
            .success(function (data) {
				console.log("LoginService signIn: data=", data);
				//save id to auth service
				//redirect
            })
            .error(function (data) {
            	console.log("LoginService signIn: data=", data);
            	//show error message and other shit for damn user
            });
	}

	return obj;
}]);