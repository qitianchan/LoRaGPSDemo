/**
 * Created by admin on 2016/3/23.
 */

$(document).ready(function(){
    var count = 0;
    var targetMarker;
    var simulateMarker;
    var target = {};
    var stations = [];
    var stationsSelected = [];
    var data = [];
    var time = [];
    var markers = [];

    var stationCount = parseInt($("input[name='stationCount']:checked").val());
    var deviation = parseInt($("input[name='deviation']:checked").val());
    $("input[name='stationCount']").change(function(){
        /*
        基站数量改变，选中的基站改变，重新绘制地图上的标记点
         */
        stationCount =  parseInt($(this).val());
        stationsSelected = stations.slice(0, stationCount);
        map.remove(markers);
        markers = [];
       $.each(stationsSelected, function(i, item) {
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
        });
        map.setFitView();

    });

    $("input[name='deviation']").change(function(){
        deviation =  parseInt($(this).val());
    });

    $('#chart').hide();
    var myChart = echarts.init(document.getElementById('chart'));

    // map
    var cluster;

    var map = new AMap.Map('mapContainer', {
        resizeEnable: true,
        center: [116.397428, 39.90923],
        zoom: 5
    });
    map.clearMap();  // 清除地图覆盖物

    // 获取基站坐标
    var aj = $.ajax({
        url: 'devices_lnglat',
        type:'get',
        cache: false,
        dataType: 'json',
        success: function(res) {
            if (res.data) {
                stations = res.data;
                $.each(res.data.slice(0, parseInt($("input[name='stationCount']:checked").val())), function (i, item) {
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

                    var newCenter = map.setFitView();

                    //marker = {position: [p.lng, p.lat], device_id: item.device_id};
                    //markers.push(marker);
                    //positions.push(p)
                });

                // 数量不够时，radio disable
                var stationCountInput = [];
                if (stations.length < 4){
                    stationCountInput = $("input[name='stationCount']").attr('disabled', 'true');
                }else if(stations.length < 6){
                    stationCountInput = $("input[name='stationCount']").slice(1).attr('disabled', 'true');
                }else if(stations.length < 8) {
                    stationCountInput = $("input[name='stationCount']").slice(2).attr('disabled', 'true');
                }
                stationsSelected = stations.slice(0, parseInt($("input[name='stationCount']:checked").val()));

                $.each(stationCountInput, function(i, item){
                    $(item.parentNode).addClass('disabled')
                });
            }
        }
    });

    var bind = function(){
      var clickListener = AMap.event.addListener(map, "click", _onClick);
    };
    document.getElementById('mapContainer').addEventListener('click', bind);
    var _onClick = function(e){
        if(!(targetMarker == undefined)){
            map.remove(targetMarker);
        }
        targetMarker = new AMap.Marker({
          position : e.lnglat,
          map : map
        });

        target.lng = e.lnglat.lng;
        target.lat = e.lnglat.lat;

        jQuery.ajax({
                    url: window.location.href,   // 提交的页面
                    data: {target: target, stations: stationsSelected, deviation: deviation, count: stationCount}, // 从表单中获取数据
                    type: "POST",                   // 设置请求类型为"POST"，默认为"GET"
                    success: function(res) {
                        $('#error').html(res.result);
                    }
                });
    };

});