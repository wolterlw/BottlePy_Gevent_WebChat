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
	obj.logOut = function() {
		$http({ method: "DELETE", url: "/users/"+AuthService.getId() })
			.then(function() {
				//remove id from AuthService
				//redirect to log-in page
				console.log("User has successfully logged out");
			}, 
			function() {
				//remove id from AuthService
				//redirect to log-in page
				console.log("User has logged out with error");
			});
	}
	return obj;
}]);

msngrServices.factory('ContactService', ['$http', 'AuthService', function($http, AuthService) {
	var obj = {}
	obj.getContacts = function(buddyList) {
		$http.get("/users/"+AuthService.getId())
			.success(function (data) {
				console.log("ContactService, getContacts: data=", data);
				buddyList = data;
			})
			.error(function(data) {
				//handle error
				console.log("ContactService, getContacts: data=", data);
			});
	}
	obj.addContact = function(buddyList, username) {
		$http.post("/users/search", username)
			.success(function(data) {
				console.log("ContactService, addContact: data=", data);
				//redirect to dialog with this user
			})
			.error(function(data) {
				//handle error
				console.log("ContactService, getContacts: data=", data);
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
	obj.goToLogin = function() {
		$location.path('/log-in');
	}
	return obj;
}]);