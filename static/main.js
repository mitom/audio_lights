angular.module('control', ['rzModule'])
    .controller('MainCtrl', function($scope, $http) {
        $scope.config = {};
        $scope.updating = false;
        $http.get('/config').then(function(resp) {
            $scope.config=resp.data;
        });

        $scope.area_slider = {
            floor: 0,
            ceil: 1,
            step: 0.01,
            precision: 2
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
