var msngr = angular.module('messenger', ['ngRoute']);

msngr.config(function ($routeProvider) {
   	$routeProvider
		.when('/log-in', {
			templateUrl: 'log-in.tmpl.html',
			controller: function() {},
			controllerAs: 'a'
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