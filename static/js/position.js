/**
 * Created by admin on 2016/7/13 0013.
 */
$(document).ready(function(){
    var stations = [];
    var data = [];
    var markers = [];
    var infoWindows = [];

    var map = new AMap.Map('mapContainer', {
        resizeEnable: true,
        center: [116.397428, 39.90923],
        zoom: 5
    });
    map.clearMap();  // 清除地图覆盖物

    function markerClick(e) {
        window.location.href = e.target.info_url;
    }
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
                    marker.info_url = item.info_url;
                    marker.eui = item.eui;
                    marker.on('click', markerClick);
                    markers.push(marker);
                    //
                    //var infoWindow = new AMap.InfoWindow({
                    //    isCustom: true,  //使用自定义窗体
                    //    content: "<h3>" + marker.name +"<h3>",
                    //    offset: new AMap.Pixel(16, -50)//-113, -140
                    //});
                    //
                    //infoWindow.open(map, marker.getPosition());
                });
                map.setFitView();
            }
        }
    });


    var socket = io.connect('http://' + document.domain + ':' + location.port + '/lnglat');
    socket.on('new', function(data){
        // 显示到地图上
        for(i=0; i< markers.length; i++){
            if(markers[i].eui == data.eui){
                markers[i].setPosition([data.lng, data.lat])
            }
        }
        //map.setFitView();
    });

});