/**
 * Created by admin on 2016/7/13 0013.
 */
$(document).ready(function(){
    var stations = [];
    var data = [];
    var markers = [];


    var map = new AMap.Map('mapContainer', {
        resizeEnable: true,
        center: [116.397428, 39.90923],
        zoom: 5
    });
    map.clearMap();  // 清除地图覆盖物

    // 获取基站坐标
    var aj = $.ajax({
        url: 'stations_lnglat',
        type:'get',
        cache: false,
        dataType: 'json',
        success: function(res) {
            if (res.data) {
                stations = res.data;
                $.each(res.data, function (i, item) {
                    var p = {};
                    p.lng = item.lng;
                    p.lat = item.lat;

                    var icon = item.icon_uri;
                    var markerPosition = [p.lng, p.lat];
                    var marker = new AMap.Marker({
                        map: map,
                        position: markerPosition,
                        icon: icon,
                        offset: {x: -8,y: -34}
                    });
                    marker.device_id = item.device_id;
                    marker.name = item.name;
                    markers.push(marker);
                    map.setFitView();
                });
            }
        }
    });


    var socket = io.connect('http://' + document.domain + ':' + location.port + '/lnglat');
    socket.on('new data', function(data){
        // 显示到地图上
        var newMarker = new AMap.Marker({
                    map: map,
                    position: [data.lng, data.lat],
                    icon: '/static/image/mark_node.png',
                    offset: {x: -8, y: -34}
                });
        newMarker.content = 'RSSI: ' + data.rssi;
        map.setCenter([data.lng, data.lat]);
    });

});