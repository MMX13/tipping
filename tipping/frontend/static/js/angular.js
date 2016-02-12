var tippingApp = angular.module("TippingApp", ['ngRoute']);

tippingApp.config(
    function($routeProvider, $httpProvider){
        $routeProvider.
            when('/', {
                templateUrl: 'static/js/templates/home.html',
                controller: 'HomeCtrl'
            }).
            when('/tips', {
                templateUrl: 'static/js/templates/tipping.html',
                controller: 'TipCtrl'
            }).
            when('/draw',{
                templateUrl: 'static/js/templates/draw.html',
                controller: 'DrawCtrl'
            }).
            otherwise({
                redirectTo: '/'
            });
        $httpProvider.defaults.xsrfCookieName = 'csrftoken';
        $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
    });

tippingApp.controller("TipCtrl", function($scope, $http){
    $scope.updateTip = function(i, tip_team){
        tip = $scope.tips[i];
        if (tip.team != tip_team) {
            // Send the update
            $http.patch("/api/tip/" + tip.id + "/", {'team': tip_team}).
                then(function () {
                    // Update the scope
                    $scope.tips[i].team = tip_team;
                });
        }
    };

    $scope.tips = [];
    $http.get("/api/tips/").
        then(function(data) {
            //console.log(data);
            $scope.tips=data.data;
        });
});

tippingApp.controller("DrawCtrl", function($scope, $http){
    draw = [];
    $http.get("/api/games/").
        then(function(data){
            $scope.draw=data.data;
        })

});

tippingApp.controller("HomeCtrl", function($scope){

});