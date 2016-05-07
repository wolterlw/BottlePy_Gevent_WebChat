var msngr = angular.module('messenger', ['ngRoute', 'cControllers']);

msngr.config(function ($routeProvider) {
   	$routeProvider
		.when('/log-in', {
			templateUrl: 'log-in.tmpl.html',
			controller: 'LoginController',
			controllerAs: 'loginCtrl'
		})
		.when('/messages', {
			templateUrl: 'messages.tmpl.html',
			controller: function() {},
			controllerAs: 'b'
		})
		.when('/dialog', {
			templateUrl: 'dialog.tmpl.html',
			controller: function() {},
			controllerAs: 'c'
		})
		.otherwise({
			redirectTo: '/log-in'
	    });
});