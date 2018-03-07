var tippingApp = angular.module("TippingApp", ['ngRoute']);


compare_tips = function(a,b) {
  if (a.game.start_time < b.game.start_time)
    return -1;
  else if (a.game.start_time > b.game.start_time)
    return 1;
  else
    return 0;
}


compare_draw = function(a, b) {
  if (a.start_time < b.start_time)
    return -1;
  else if (a.start_time > b.start_time)
    return 1;
  else
    return 0;
}


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
            when('/past', {
                templateUrl: 'static/js/templates/past.html',
                controller: 'PastTipCtrl'
            }).
            when('/draw',{
                templateUrl: 'static/js/templates/draw.html',
                controller: 'DrawCtrl'
            }).
            when('/scores',{
                templateUrl: 'static/js/templates/scores.html',
                controller: 'ScoreCtrl'
            }).
            when('/ladder',{
                templateUrl: 'static/js/templates/ladder.html',
                controller: 'LadderCtrl'
            }).
            when('/help',{
                templateUrl: 'static/js/templates/help.html'
            }).
            otherwise({
                redirectTo: '/'
            });
        $httpProvider.defaults.xsrfCookieName = 'csrftoken';
        $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
    });

tippingApp.controller("NavCtrl", function($scope, $location){
    $scope.location = $location;
});

tippingApp.controller("HomeCtrl", function($scope, $http){
    $scope.prev = null;
    $scope.next = null;
    $scope.loaded = false;

    check_tip = function(x){
        if(x.game.status != 'C' || x.team == null){
            return false;
        }
        if((x.game.home_score >= x.game.away_score) && (x.team.name == x.game.home_team.name)){
            return true;
        }
        if((x.game.home_score <= x.game.away_score) && (x.team.name == x.game.away_team.name)){
            return true;
        }
        return false;
    }

    updateGame = function(){
        $http.get("/api/tips/").
            then(function(data){
                tips = data.data
                $scope.next = tips.filter(x => x.game.status=='P')
                                          .sort((a, b) => a.game.start_time > b.game.start_time)[0]
                $scope.game = $scope.next.game
                $scope.num_games = tips.length
                $scope.num_games_played = tips.filter(x => x.game.status=='C').length
                $scope.num_correct = tips.filter(check_tip).length
                $scope.loaded = true
            })
    }
    updateGame()
});

tippingApp.controller("ScoreCtrl", function($scope, $http){

    $scope.max_round = 0;

    $scope.getScores = function(){
        $http.get("/api/scores/").
            then(function(data){
                scores = data.data

                users=[];
                rounds=[];
                userscores = {};
                usertotals=[];
                $scope.rounds=[];

                scores.forEach(function(s){
                    if (users.indexOf(s.username)==-1){
                        users.push(s.username);
                        userscores[s.username] = {};
                        usertotals[s.username] = 0;
                    }
                    if (rounds.indexOf(s.round)==-1){
                        rounds.push(s.round);
                        $scope.rounds.push({'round':s.round});

                        //Refactor this out
                        if (s.round>$scope.max_round){
                            $scope.max_round=s.round;
                        }

                    }
                    userscores[s.username][s.round]=s.score;

                });
                console.log(userscores)

                users.forEach(function(u){
                    total = 0
                    for(x=1;x<=rounds.length;x++){
                        total+=userscores[u][x];
                    }
                    usertotal = {'user':u, 'total':total};
                    usertotals.push(usertotal)
                });

                $scope.usertotals = usertotals
                $scope.userscores = userscores

            });

    }

    $scope.getScores()
});

tippingApp.controller("TipCtrl", function($scope, $http){


    $scope.submitting = {}

    $scope.updateTip = function(i, tip_team){
        tip = $scope.tips[i];

        if (tip.team != tip_team) {
            // Send the update
            $scope.submitting[tip.game.fixture_id] = true;
            $http.patch("/api/tip/" + tip.id + "/", {'team': tip_team.id}).
                then(function () {
                    // Update the scope
                    $scope.tips[i].team = tip_team;
                    $scope.submitting[tip.game.fixture_id] = false;
                });
        }
    };

    $scope.tips = [];
    $http.get("/api/tips/").
        then(function(data) {
            $scope.tips = data.data.sort(compare_tips);
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
                $scope.draw=data.data.sort(compare_draw);
                $scope.round=$scope.draw[0].round;
            })
    }

    $scope.changeRound = function(change){
        round = $scope.round+change;
        if ((round>0) && (round<29)){
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


tippingApp.controller("PastTipCtrl", function($scope, $http){
    $scope.show = -1;

    function compare(a,b) {
      if (a.game.start_time < b.game.start_time)
        return -1;
      else if (a.game.start_time > b.game.start_time)
        return 1;
      else
        return 0;
    }

    $scope.updatePastTips = function(round){
        if (round!=""){
            round="?round="+round;
        }
        $http.get("/api/tips/"+round).
            then(function(data){
                $scope.pasttips=data.data.sort(compare_tips);
                $scope.round=$scope.pasttips[0].round;
            });
    }

    $scope.changeRound = function(change){
        console.log('Change: '+change);
        round = $scope.round+change;
        console.log('New round: '+round);
        console.log('Current round: '+$scope.current_round)
        if ((round>0) && (round<=$scope.current_round)){
            console.log('Success');
            $scope.updatePastTips(round)
        }
    }

    $scope.showDetails = function(id){
        if ($scope.show == id){
            $scope.show = -1;
        } else {
            $scope.show = id;
        }
    }

    $http.get("/api/round/").
        then(function(data){
            $scope.current_round=data.data["round"];
            $scope.updatePastTips("")
        });


});

tippingApp.controller('LadderCtrl', function($scope, $http){

    $http.get("/api/ladder").
        then(function(data){
            $scope.ladder=data.data;
        });
});

tippingApp.controller('HelpCtrl', function(){
});