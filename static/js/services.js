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
				AuthService.removeId();
				PathService.goToLogin();
				console.log("User has successfully logged out");
			}, 
			function() {
				AuthService.removeId();
				PathService.goToLogin();
				console.log("User has logged out with error");
			});
	}
	return obj;
}]);

msngrServices.factory('ContactService', ['$http', '$q', 'AuthService', 'PathService', function($http, $q, AuthService, PathService) {
	var obj = {}
	obj.getContacts = function() {
		var deferred = $q.defer();
		$http.get("/users/"+AuthService.getId())
			.success(function (data) {
				console.log("ContactService, getContacts: data=", data);
				deferred.resolve(data);
			})
			.error(function(data) {
				//handle error
				console.log("ContactService, getContacts: data=", data);
				deferred.reject(data);
			});
		return deferred.promise;
	}
	obj.addContact = function(username) {
		$http.post("/users/search", username)
			.success(function(data) {
				console.log("ContactService, addContact: data=", data);
				//create new dialog via api using DialogService
				PathService.goToDialog(username.username);
			})
			.error(function(data) {
				//handle error
				console.log("ContactService, addContact: data=", data);
			});
	}
	return obj;
}]);

//internal services
msngrServices.factory('AuthService', function() {
	var id;
	var obj = {};
	obj.setId = function(idToSet) {
		id = idToSet;
	}
	obj.getId = function() {
		return id;
	}
	obj.removeId = function() {
		id = undefined;
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
	obj.goToDialog = function(user) {
		if(user) $location.path('/dialog/'+user);
	}
	return obj;
}]);