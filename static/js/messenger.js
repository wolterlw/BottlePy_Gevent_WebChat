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
		.when('/dialog/:user', {
			templateUrl: 'view/dialog.view.html',
			controller: 'DialogController',
			controllerAs: 'dialogCtrl'
		})
		.otherwise({
			redirectTo: '/log-in'
	    });
});