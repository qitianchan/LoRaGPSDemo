/**
 * Created by admin on 2016/3/23.
 */

$(document).ready(function(){
    //$('#submit').hide();
    var targetMarker;
    var count = 0;
    // icheck
    var checked_list = $('#checkedForm');
    //$('input').iCheck('check');
    $('input').on('ifChecked', function(event){
        var targetID = event.target.name.split("_")[1];
        var inputName = 'device_' + targetID;
        var i = '#' + 'label_' + targetID;
        var labelVal = $(i).html().trim();
        var formInput = '#' + inputName;
        if($(formInput).length == 0) {
            var groupID = 'group_' + targetID;
            var html = '<div class="form-group" id='+ groupID + '><label for='+ inputName + '>'+ labelVal + '</label>' +
                '<input type = "text" class = "form-control" id='+ inputName + ' name=' + inputName
                 + ' placeholder="请输入飞行时间"></div>';
            var child = $(html);
            checked_list.append(child);
        }

    });
  $('input').iCheck({
    checkboxClass: 'icheckbox_flat-green',
    radioClass: 'iradio_flat-green'
  });
   $('input').on('ifUnchecked', function(event){
       var targetID = event.target.name.split("_")[1];
       var formTargetID = '#group_' + targetID;
       $(formTargetID).remove();
   });


    // map
    var cluster, markers = [];

    var map = new AMap.Map('mapContainer', {
        resizeEnable: true,
        center: [116.397428, 39.90923],
        zoom: 5
    });
    map.clearMap();  // 清除地图覆盖物

    // todo: 显示不同状态的垃圾桶标志， 超过80%的用红图标标志
    // todo: 设备在地图上的同步信息
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
                    p.occupancy = item.occupancy;
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
                    marker.on('click', markerClick);
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
    var markerClick = function(e) {
        var name = e.target.name || e.target.device_id;
        var inputName = 'device_' + e.target.device_id;
        var formInput = '#' + inputName;
        var groupID = 'group_' + e.target.device_id;
        var checkbox = '#' + 'checkbox_' + e.target.device_id;
        if($(formInput).length == 0) {
            var html = '<div class="form-group" id="'+ groupID + '" ><label for='+ inputName + '>'+ name + '</label>' +
            '<input type = "text" class = "form-control" id='+ inputName + ' name=' + inputName
             + ' placeholder="请输入飞行时间"></div>';
            var child = $(html);
            checked_list.append(child);
        }
        $(checkbox).addClass('checked');

    };

    function addCluster(markers) {
        if (cluster) {
            cluster.setMap(null);
        }
        map.plugin(["AMap.MarkerClusterer"], function() {
            cluster = new AMap.MarkerClusterer(map, markers);
        });
    }

    // form submit
    $('#submit').click(function(){
                jQuery.ajax({
                    url: window.location.href,   // 提交的页面
                    data: $('form').serialize(), // 从表单中获取数据
                    type: "POST",                   // 设置请求类型为"POST"，默认为"GET"
                    success: function(res) {
                        if(!(targetMarker == undefined)){
                            map.remove(targetMarker);
                        }
                        var markerPosition = [res.lng, res.lat];
                        targetMarker = new AMap.Marker({
                            map:map,
                            position: markerPosition,
                            icon: "http://lbs.amap.com/wp-content/uploads/2014/06/marker.png",
                            offset: {x: -8,y: -34}
                        });
                        map.setCenter(markerPosition);

                    },
                    error: function(res) {
                        var message = res.responseJSON.message;
                    }
                });
    });

});