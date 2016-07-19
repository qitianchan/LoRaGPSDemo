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
        url: 'position_records',
        type:'post',
        cache: false,
        data: {device_eui: $('#device-info').data('eui')},
        success: function(res) {
            if (res.data) {
                $.each(res.data, function (i, item) {
                    var p = {};
                    p.lng = item.lng;
                    p.lat = item.lat;

                    var markerPosition = [p.lng, p.lat];
                    var marker = new AMap.Marker({
                        map: map,
                        position: markerPosition,
                        icon: '/static/image/mark_node.png',
                        offset: {x: -8,y: -34}
                    });
                    marker.device_id = item.device_id;
                    marker.name = item.name;
                    markers.push(marker);
                });
                markers[markers.length -1].setIcon('/static/image/mark_station.png');
                map.setFitView();
            }
        }
    });


    var socket = io.connect('http://' + document.domain + ':' + location.port + '/lnglat/' + $('#device-info').data('eui'));
    socket.on('new data', function(data){
        // 更换图标
        markers[markers.length -1].setIcon('/static/image/mark_node.png');
        // 如果数据多于30个，删除第一个mark
        if(markers.length >= 30){
            map.remove([markers.shift()]);
        }
        // 添加新marker显示到地图上
        var newMarker = new AMap.Marker({
                    map: map,
                    position: [data.lng, data.lat],
                    icon: '/static/image/mark_station.png',
                    offset: {x: -8, y: -34}
        });
         // 更换图标
        markers[markers.length -1].setIcon('/static/image/mark_node.png');
        //newMarker.content = 'createTime: ' + data.create_time;
        markers.push(newMarker);
        map.setCenter([data.lng, data.lat]);
    });
});