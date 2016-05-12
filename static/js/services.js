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

msngrServices.factory('ContactService', ['$http', '$q', 'AuthService', 'PathService', 'DialogService', function($http, $q, AuthService, PathService, DialogService) {
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
				DialogService.createDialog(data.id)
				PathService.goToDialog(username.username);
			})
			.error(function(data) {
				//handle error
				console.log("ContactService, addContact: data=", data);
			});
	}
	return obj;
}]);

msngrServices.factory('DialogService', ['$http', '$q', 'AuthService', function($http, $q, AuthService) {
	var dialogId;
	var obj = {};
	obj.setDialogId = function(id) {
		dialogId = id;
		console.log("DialogService, setDialogId, dialogId=", dialogId);
	}
	obj.getDialogId = function() {
		console.log("DialogService, getDialogId, dialogId=", dialogId);
		return dialogId;
	}
	obj.createDialog = function(toId) {
		var self = this;
		$http({ method: "PUT", url: "/dialogues/"+toId, data: {'id': AuthService.getId()} })
			.then(function(response) {
				self.setDialogId(response.data.dialogue_id);
				console.log("DialogService, createDialog method, sendId=", AuthService.getId());
				console.log("DialogService, createDialog method, toId=", toId);
				console.log("DialogService, createDialog method, response=", response);
				console.log("DialogService, createDialog method, self.dialogId=", self.getDialogId());
			}, 
			function(response) {
				//handle error
				console.log("DialogService, createDialog method, response=", response);
			});
	}
	obj.getMessageHistory = function() {
		var self = this;
		var deferred = $q.defer();
		$http.post("/dialogues/"+self.getDialogId(), {'id': AuthService.getId()})
			.success(function (data) {
				console.log("DialogService, getMessageHistory: data=", data);
				deferred.resolve(data);
			})
			.error(function(data) {
				//handle error
				console.log("DialogService, getMessageHistory: data=", data);
				deferred.reject(data);
			});
		return deferred.promise;
	}
	obj.postMessage = function(msgBody) {
		var date = (new Date).getFullYear() +"-"+ ((new Date).getMonth()+1) +"-"+(new Date).getDate() +" ";
		date += (new Date).getHours() +":"+ (new Date).getMinutes() +":"+ (new Date).getSeconds();
		var dataToSend = {'id': AuthService.getId(), datetime: date, 'body': msgBody};
		var deferred = $q.defer();
		$http.post("/dialogues/"+this.getDialogId()+"/messages_text", dataToSend)
			.success(function(data) {
				console.log("DialogService, sendMessage, data=", data);
				deferred.resolve(data);
			})
			.error(function(data) {
				console.log("DialogService, sendMessage, data=", data);
				//handle error
				deferred.reject(data);
			})
		return deferred.promise;	
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