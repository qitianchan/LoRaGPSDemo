/**
 * Created by admin on 2016/3/23.
 */

$(document).ready(function(){
    var count = 0;
    var targetMarker;
    var simulateMarker;
    var target = {};
    var stations = [];
    var data = [];
    var time = [];
    $('#chart').hide();
    var myChart = echarts.init(document.getElementById('chart'));



    // map
    var cluster, markers = [];

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
                $.each(res.data, function (i, item) {
                    var p = {};
                    p.lng = item.lng;
                    p.lat = item.lat;
                    stations.push(p);

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

                //addCluster(markers);
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
                    data: {target: target, stations: stations}, // 从表单中获取数据
                    type: "POST",                   // 设置请求类型为"POST"，默认为"GET"
                    success: function(res) {
                        $('#chart').show();
                        if(!(simulateMarker == undefined)){
                            map.remove(simulateMarker);
                        }
                        var markerPosition = [res.lng, res.lat];
                        simulateMarker = new AMap.Marker({
                            map:map,
                            position: markerPosition,
                            icon: "http://lbs.amap.com/wp-content/uploads/2014/06/marker.png",
                            offset: {x: -8,y: -34}
                        });
                        map.setCenter(markerPosition);
                        var thtml = '<p>实际位置:(' + target.lng + ', '+ target.lat + ')' +'</p>';
                        var shtml = '<p>估算位置:(' + res.lng + ', '+ res.lat + ')' +'</p>';
                        var phtml = '<p>定位误差: ' + res.error + '(m)' +'</p>';
                        $('#simulateInfo').empty();
                        $('#simulateInfo').append(thtml);
                        $('#simulateInfo').append(shtml);
                        $('#simulateInfo').append(phtml);

                        // data
                        var record = res.record;
                        time = [];
                        data = [];
                        option = {
                            title: {
                                text: '模拟迭代图'
                            },
                            tooltip: {
                                trigger: 'axis',
                                formatter: function (params) {
                                    params = params[0];
                                    myChart.setOption(option);

                                    return params.name + '：' + params.value + '(米)';
                                },
                                axisPointer: {
                                    animation: false
                                }
                            },
                            xAxis: {
                                type : 'category',
                                name: '迭代次数',
                                nameLocation: 'middle',
                                nameGap: 20,
                                nameTextStyle: {
                                    color: '#000',
                                    fontSize: 16
                                },
                                boundaryGap : false,
                                axisLine: {onZero: false},
                                data: time
                            },
                            yAxis: {
                                type: 'value',
                                name: '定位误差（米）',
                                nameTextStyle: {
                                    color: '#000',
                                    fontSize: 16
                                },
                                boundaryGap: [0, '100%'],
                                splitLine: {
                                    show: false
                                }
                            },
                            series: [{
                                name: '模拟数据',
                                type: 'line',
                                showSymbol: false,
                                hoverAnimation: false,
                                data: data
                            }],
                            color: '#FBEFD5'
                        };
                        record.forEach(function(item, i){
                            time.push(i+1 + 'th');
                            data.push(item)
                        });


                        myChart.setOption(option);

                    },
                    error: function(res) {

                    }
                });
    };

});