var msngrDirectives = angular.module('cDirectives', []);

msngrDirectives.directive('signIn', function() {
	return {
		restrict: 'E',
		templateUrl: 'template/sign-in.tmpl.html',
		controller: 'SignInController',
		controllerAs: 'signInCtrl'
	};
});
msngrDirectives.directive('signUp', function() {
	return {
		restrict: 'E',
		templateUrl: 'template/sign-up.tmpl.html',
		controller: 'SignUpController',
		controllerAs: 'signUpCtrl'
	};
});