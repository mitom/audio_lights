angular.module('control', ['rzModule'])
    .controller('MainCtrl', function($scope, $http) {
        $scope.config = {};
        $scope.updating = false;
        $http.get('/config').then(function(resp) {
            $scope.config=resp.data;
        });

        var music = {
            "profile": "music",
            "trim":5,
            "saturation":3000,
            "scale":100,
            "b_area":[0.6,1],
            "clapper":true,
            "b_boost":[0,1,1.7],
            "sample_size":64,
            "g_boost":[0,1,1.9],
            "active":true,
            "r_area":[0.33,0.7],
            "r_boost":[0,1,1.6],
            "g_area":[0.04,0.3]
        };

        var speech = {
            "profile": "speech",
            "trim":10,
            "saturation":7050,
            "scale":100,
            "b_area":[0.29,0.53],
            "clapper":false,
            "b_boost":[0,1,3.1],
            "sample_size":64,
            "g_boost":[0.13,0.21,2.7],
            "active":true,
            "r_area":[0.23,0.54],
            "r_boost":[0,1,2.1],
            "g_area":[0,0.22]
        };
        $scope.settings = {
            "speech": speech,
            "music": music
        };

        $scope.load = function (profile) {
            $scope.config = $scope.settings[profile];
            $scope.update();
        };


        $scope.profile = {};

        $scope.area_slider = {
            floor: 0,
            ceil: 1,
            step: 0.01,
            precision: 2
        };

        $scope.toggle = function() {
            $scope.config.active = !$scope.config.active;
            $scope.update();
        };

        $scope.update = function() {
            $scope.updating = true;
            $http.post('/config', $scope.config).then(function() {
                $scope.updating = false;
            }, function() {
                $scope.updating = false;
            })
        };
        $scope.reset = function() {
            $http.post('/reset_config').then(function(resp) {
                $scope.config=resp.data;
            })
        }
    });
