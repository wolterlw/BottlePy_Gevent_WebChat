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

msngrControllers.controller('MessagesController', ['ContactService', 'PathService', 'DialogService', function(ContactService, PathService, DialogService) {
	//have no idea where it supposed to be
	$("#menu-toggle").fadeIn(0);

	var self = this;
	this.newFriend = "";
	this.buddyList = {};
	this.friends = [];

	ContactService.getContacts()
		.then(function(data) {
			angular.forEach(data, function(key, value) {
				self.friends.push(key);
				self.buddyList[key] = value;
			});
			console.log("MessagesController, ContactService.getContacts.then self.buddyList=", self.buddyList);
			console.log("MessagesController, ContactService.getContacts.then self.friends=", self.friends);
		}, function(data) {
			//handle error
			console.log("MessagesController, ContactService.getContacts.then data=");
		});

	this.search = function() {
		username = {'username': this.newFriend};
		console.log("MessagesController, search, username=", username);
		ContactService.addContact(username);
	}
	this.openDialog = function(user) {
		console.log("MessagesController, openDialog, user=", user);
		DialogService.setDialogId(this.buddyList[user]);
		PathService.goToDialog(user);
	}
}]);

msngrControllers.controller('DialogController', ['DialogService', 'AuthService', function(DialogService, AuthService) {
	var self = this;
	var msgs;

	DialogService.getMessageHistory().then(function(data) {
		console.log("DialogController, data=", data);
		self.msgs = data[DialogService.getDialogId()];
		console.log("DialogController, self.msgs=", self.msgs);
	}, function(data) {
		//handle error
		console.log("DialogController, data=", data);
	});

	this.isIdMatch = function(id) {
		return (AuthService.getId() == id); 
	}
	this.setRightHeader = function(id) {
		if(this.isIdMatch(id)) return "text-right"
		else return "";
	}
}]);