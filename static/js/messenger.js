var msngr = angular.module('messenger', ['ngRoute', 'cControllers', 'cDirectives', 'cServices']);

msngr.config(function ($routeProvider) {
   	$routeProvider
		.when('/log-in', {
			templateUrl: 'view/log-in.view.html',
			controller: 'LoginController',
			controllerAs: 'loginCtrl'
		})
		.when('/messages', {
			templateUrl: 'view/messages.view.html',
			controller: 'MessagesController',
			controllerAs: 'messagesCtrl'
		})
		.when('/dialog', {
			templateUrl: 'view/dialog.view.html',
			controller: function() {},
			controllerAs: 'c'
		})
		.otherwise({
			redirectTo: '/log-in'
	    });
});