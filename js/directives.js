var msngrDirectives = angular.module('cDirectives', []);

msngrDirectives.directive('signUp', function() {
	return {
		restrict: 'E',
		templateUrl: 'template/sign-up.tmpl.html',
		controller: 'SignUpController',
		controllerAs: 'signUpCtrl'
	};
});