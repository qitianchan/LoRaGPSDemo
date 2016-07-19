# coding: utf-8
from __future__ import division
from websocket import create_connection
from redis import StrictRedis
import sqlite3
import json
import time
import traceback   # find error
from socketIO_client import SocketIO, BaseNamespace
from config import LORA_HOST, LORA_PORT, LORA_APP_EUI, LORA_TOKEN
from binascii import unhexlify, hexlify
from threading import Thread
from config import DefaultConfig
import math
from extentions import io
import logging
import datetime

message_logger = logging.getLogger('message')
message_logger.setLevel(logging.DEBUG)

socketio_logger = logging.getLogger('socketio')
socketio_logger.setLevel(logging.DEBUG)


formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

f_message_handle = logging.FileHandler(DefaultConfig.MSG_FILE_LOG)
f_message_handle.setLevel(logging.INFO)
f_message_handle.setFormatter(formatter)
f_socketio_handle = logging.FileHandler(DefaultConfig.SOCKETIO_FILE_LOG)
f_socketio_handle.setLevel(logging.INFO)


stream_handle = logging.StreamHandler()
stream_handle.setLevel(logging.DEBUG)
stream_handle.setFormatter(formatter)

message_logger.addHandler(f_message_handle)
message_logger.addHandler(stream_handle)
socketio_logger.addHandler(f_socketio_handle)
socketio_logger.addHandler(stream_handle)

pi = math.pi
a = 6378245.0
ee = 0.00669342162296594323

cx = sqlite3.connect(DefaultConfig.DATABASE_PATH)

DEVS_EUI = ['BE7A0000000003A1', 'BE7A0000000003A4', 'BE00000000000005']

TIME_LIMIT = 172000         # which means 13:40:00
HOST = LORA_HOST
APP_EUI = LORA_APP_EUI
TOKEN = LORA_TOKEN
PORT = LORA_PORT
def listen_thread():
    try:
        print('hello listen thread')
        thread = Thread(target=listen_data)
        thread.start()
    except Exception as e:
        print('Something wrong in listen_thread: %s' % e)
        listen_thread()



def listen_data():
    socketio_cli = SocketIO(host=HOST, port=PORT, params={'app_eui': APP_EUI, 'token': TOKEN})
    test_namespace = socketio_cli.define(TestNamespace, '/test')


class TestNamespace(BaseNamespace):

        def on_connect(self):
            socketio_logger.debug('socket io connected')

        def on_disconnect(self):
            print('socket io disconnected')

        def on_error_msg(self):
            print('error occured')
            print(self)

        def on_post_rx(self, msg):
            print('get post msg')
            try:
                cook_rx_message(msg)
            except Exception as e:
                raise e

        def on_enqueued(self):
            print('enqueued')
            print(self)

        def on_connect_error(self, msg):
            print('connect error')
            print(msg)


def cook_rx_message(data):
    """
    处理接收到的信息
    :param message:
    :return:
    """

    # cx = sqlite3.connect(DefaultConfig.DATABASE_PATH)
    global cx
    if data['EUI'].upper() in get_nodes(cx):
        message_logger.debug(json.dumps(data))
        format = '%Y%m%d %H%M%S'
        value = time.localtime(data['ts']/1000)
        btime = time.strftime(format, value)
        payload = data['data']
        rssi = data['rssi']
        snr = data['snr']
        seq = data['fcnt']
        freq = data['freq']
        lnglat = (0, 0)
        if payload != '000000000000':

            try:
                lnglat = get_lnglat(payload, 0)
            except Exception as e:
                raise e
                # print('parse payload wrong')

            message_logger.info('EUI:{0}- payload:{1} - lng:{2} - lat:{3} '.format(data['EUI'], data['data'], lnglat[0], lnglat[1]))

            test_data = (None, data['EUI'].upper(), lnglat[0], lnglat[1], rssi, snr, seq, freq, time.time(), None)

            try:
                # 记录收到的数据
                position_record = (None, datetime.datetime.now(), lnglat[0], lnglat[1], data['EUI'].upper())
                record_postion(cx, position_record)

                # 发送给前端数据
                io.emit('new data', {'eui': test_data[1], 'lng': test_data[2], 'lat': test_data[3], 'rssi': test_data[4],
                                     'snr': test_data[5], 'seq': test_data[6], 'freq': test_data[7], 'createtime': test_data[8],
                                     'datetime': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(test_data[8]))},
                        namespace='/lnglat/' + data['EUI'])
                # 发送全部
                io.emit('new', {'eui': data['EUI'], 'lng': lnglat[0], 'lat': lnglat[1], 'createtime': test_data[8]},
                        namespace='/lnglat')

                socketio_logger.debug('emit new data')
                socketio_logger.info('lng:{0} - lat:{1}'.format(lnglat[0], lnglat[1]))

            except Exception as e:
                print('save data error. %s' % e)




def get_lnglat(payload, dev_type):
    """
    get longitude and latitude from payload.
    DO NOT ASK me what different between longitude and longitude1 !!!
    :param payload: payload
    :param dev_type: device type
    :return: (longitude, latitude)
    """
    longitude = -1
    latitude = -1
    try:
        if dev_type == 0:
            latitude = int(payload[0:6],16)*90.0/8388607
            longitude = int(payload[6:12],16)*180.0/8388607
        elif dev_type == 1:
            # 萌宝设备
            data = unhexlify(payload.encode(encoding='utf-8', errors='strict'))
            data = data.decode(encoding='utf-8', errors='strict')
            lst = data.split(',')
            latitude = float(lst[0])/100
            latitude = round(latitude)+(latitude-round(latitude))*100/60
            longitude = float(lst[2])/100
            longitude = round(longitude)+(longitude-round(longitude))*100/60
        elif dev_type == 2:
            # BE00000000000005
            #todo: 转换格式
            lng_lat = [float(item) for item in unhexlify(payload).decode('utf-8').split(',')]
            try:
                latitude = lng_lat[0] + lng_lat[1] / 60
                longitude = lng_lat[2] + lng_lat[3] / 60
            except IndexError:
                pass
            except TypeError as e:
                pass

    except Exception as e:
        latitude = int(payload[16:22],16)*90.0/8388607
        longitude = int(payload[22:28],16)*180.0/8388607
    if longitude == -1 or latitude == -1:
        return (-1, -1)
    # return (longitude, latitude)
    return gps2gd((longitude, latitude))


def gps2gd(lnglat):
    """
    gps坐标转高德地图坐标
    :param lnglat: (longitude, latitude)
    :return:  (longtitude, latitude)
    """
    wglng = lnglat[0]
    wglat = lnglat[1]

    dlng = trans_lng((wglng-105.0, wglat-35.0))
    dlat = trans_lat((wglng-105.0, wglat-35.0))
    radlat = wglat / 180 * pi
    magic = math.sin(radlat)
    magic = 1 - ee * magic * magic
    sqrtMagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtMagic) * pi)
    dlng = (dlng * 180.0) / (a / sqrtMagic * math.cos(radlat) * pi)
    lat = wglat + dlat
    lng = wglng + dlng
    return (lng, lat)

def trans_lng(lnglat):
    """
    精度转换
    :param longitude:
    :return:
    """
    x = lnglat[0]
    y = lnglat[1]
    ret = 300.0 + x + 2.0 * y + 0.1 * x * x + 0.1 * x * y + (0.1* math.sqrt(abs(x)))
    ret += (20.0 * math.sin(6.0 * x * pi) + 20.0 * math.sin(2.0 * x * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(x * pi) + 40.0 * math.sin(x / 3.0 * pi)) * 2.0 / 3.0
    ret += (150.0 * math.sin(x / 12.0 * pi) + 300.0 * math.sin(x / 30.0* pi)) * 2.0 / 3.0
    return ret

def trans_lat(lnglat):
    """
    纬度转换
    :param lnglat:
    :return:
    """
    x = lnglat[0]
    y = lnglat[1]
    ret = -100.0 + 2.0 * x + 3.0 * y + 0.2 * y * y + 0.1 * x * y + (0.2 * math.sqrt(abs(x)))
    ret += (20.0 * math.sin(6.0 * x * pi) + 20.0 * math.sin(2.0 * x * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(y * pi) + 40.0 * math.sin(y / 3.0 * pi)) * 2.0 / 3.0
    ret += (160.0 * math.sin(y / 12.0 * pi) + 320 * math.sin(y * pi / 30.0)) * 2.0 / 3.0
    return ret


# 数据库操作
def get_nodes(cx):
    exe = 'SELECT eui FROM devices WHERE type = 2'
    return [node[0] for node in cx.execute(exe).fetchall()]

# 更新并且记录位置
def record_postion(cx, value):
    # update
    update_exe = 'UPDATE devices SET lng={0}, lat={1} WHERE eui="{2}"'.format(value[2], value[3], value[4])
    cx.execute(update_exe)
    # 记录
    exe = 'INSERT INTO position_record VALUES (?, ?, ?, ?, ?)'
    cx.execute(exe, value)

    cx.commit()

if __name__ == '__main__':
    # socketio_cli = SocketIO(host=HOST, port=PORT, params={'app_eui': APP_EUI, 'token': TOKEN})
    # test_namespace = socketio_cli.define(TestNamespace, '/test')
    # socketio_cli.wait()
    # print(get_lnglat('0001020304050607205BDE50C9660012', 0))
    # print(get_lnglat('323234352E31343530342C4E2C31313333362E34323236382C45', 1))
    print(record_postion(cx, (None, datetime.datetime.now(), 116.362, 39.872, 'BE7A0000000003A4')))