var msngrServices = angular.module('cServices', []);

msngrServices.factory('LoginService', ['$http', 'AuthService', 'PathService', function($http, AuthService, PathService) {
	var obj = {};
	obj.signIn = function(credentials) {
		$http.post('/login', credentials)
            .success(function (data) {
				console.log("LoginService, signIn: data=", data);
				AuthService.setId(data.id);
				PathService.goToMessages();
            })
            .error(function (data) {
            	console.log("LoginService, signIn: data=", data);
            	//show error message and other shit for damn user
            });
	}
	obj.signUp = function(credentials) {
		$http.post('/register', credentials)
            .success(function (data) {
				console.log("LoginService, signUp: data=", data);
				AuthService.setId(data.id);
				PathService.goToMessages();
            })
            .error(function (data) {
            	console.log("LoginService, signUp: data=", data);
            	//show error message and other shit for damn user
            });
	}
	return obj;
}]);

msngrServices.factory('AuthService', function() {
	var id;
	var obj = {};
	obj.setId = function(idToSet) {
		id = idToSet;
	}
	obj.getId = function() {
		return id;
	}
	return obj;
});

msngrServices.factory('PathService', ['$location', function($location) {
	var obj = {};
	obj.goToMessages = function() {
		$location.path('/messages');
	}
	return obj;
}]);