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
            when('/scores',{
                templateUrl: 'static/js/templates/scores.html',
                controller: 'ScoreCtrl'
            }).
            otherwise({
                redirectTo: '/'
            });
        $httpProvider.defaults.xsrfCookieName = 'csrftoken';
        $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
    });

tippingApp.controller("BaseCtrl", function($scope, $location){
    $scope.location = $location;
});

tippingApp.controller("ScoreCtrl", function($scope, $http){
    $scope.getScores = function(){
        $http.get("/api/scores/").
            then(function(data){
                scores = data.data

                users=[];
                rounds=[];
                userscores = {};
                usertotals={};

                scores.forEach(function(s){
                    if (users.indexOf(s.username)==-1){
                        users.push(s.username);
                        userscores[s.username] = {};
                        usertotals[s.username] = 0;
                    }
                    if (rounds.indexOf(s.round)==-1){
                        rounds.push(s.round);
                    }
                    userscores[s.username][s.round]=s.score;

                });
                console.log(userscores)

                users.forEach(function(u){
                    for(x=1;x<=rounds.length;x++){
                        usertotals[u]+=userscores[u][x];
                    }
                });

                $scope.usertotals = usertotals
                $scope.userscores = userscores
                $scope.rounds = rounds


            });

    }

    $scope.getScores()
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
    $scope.show = -1;

    $scope.updateDraw = function(round){
        if (round!=""){
            round="?round="+round;
        }
        $http.get("/api/games/"+round).
            then(function(data){
                $scope.draw=[];
                $scope.draw=data.data;
                console.log($scope.draw)
                console.log($scope.draw[0].round);
                $scope.round=$scope.draw[0].round;
            })
    }

    $scope.changeRound = function(change){
        round = $scope.round+change;
        if ((round>0) && (round<29)){
            console.log(round)
            $scope.updateDraw(round)
        }
    }

    $scope.showDetails= function(id){
        if ($scope.show == id){
            $scope.show = -1;
        } else {
            $scope.show = id;
        }
    }


    $scope.updateDraw("")

});

tippingApp.controller("HomeCtrl", function($scope){

});