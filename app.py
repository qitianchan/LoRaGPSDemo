from flask import Flask, render_template, redirect, url_for, jsonify, request
from config import DefaultConfig
from model import Device
from flask_sqlalchemy import SQLAlchemy
from extenction import db
from config import NODE, BASESTATION, NODE_IMG_URI, BASESTATION_IMG_URI
from flask_wtf import Form
from wtforms.fields import StringField, TextAreaField, SelectField, FloatField, IntegerField
from simulate import get_position, simulate_position_v2

class DeviceProfileForm(Form):
    longitude = FloatField(u'longitude')
    latitude = FloatField(u'latitude')
    type = SelectField(u'type')
    name = StringField(u'name')

    def save_form(self, device):
        if isinstance(device, Device):
            device.lng = float(self.longitude.data)
            device.lat = float(self.latitude.data)
            device.type = int(self.type.data)
            device.name = self.name.data
            device.save()
        else:
            raise ValueError()


def create_app():
    app = Flask(__name__)
    app.config.from_object(DefaultConfig)
    db.init_app(app)
    with app.app_context():
        # Extensions like Flask-SQLAlchemy now know what the "current" app
        # is while within this block. Therefore, you can now run........
        db.create_all()
    return app
app = create_app()


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        target = {}
        stations = []
        data = request.form.to_dict()
        target = [float(data['target[lng]']), float(data['target[lat]'])]
        standard_deviation = int(data['deviation'])

        for i in range(int(data['count'])):
            key_lng = 'stations[' + str(i) + '][lng]'
            key_lat = 'stations[' + str(i) + '][lat]'
            station = [float(data[key_lng]), float(data[key_lat])]
            stations.append(station)
        res = simulate_position_v2(target, stations, standard_deviation)

        return jsonify({'result': res})
    devices = Device.get_base_station()
    return render_template('index.html', devices=devices)

@app.route('/devices')
def devices():
    devices = Device.get_devices()
    return render_template('devices.html', devices=devices)


@app.route('/edit/<device_id>', methods=['GET', 'POST'])
def edit(device_id):
    device = Device.get(device_id)
    if not device:
        device = Device()
    form = DeviceProfileForm()
    form.type.choices = [('1', u'Base Station'), ('2', u'Node')]
    if request.method == 'POST':
        form.save_form(device)
        return redirect(url_for('devices'))
    return render_template('edit.html', form=form, device=device)


@app.route('/delete/<device_id>')
def delete(device_id):
    Device.delete(device_id)
    return redirect(url_for('devices'))


@app.route('/devices_lnglat',  methods=['GET'])
def devices_lnglat():
    data = []
    devices = Device.get_devices()
    stations = []
    x_list = '113.5800  113.5800  113.5395  113.5395  113.5800  113.6205  113.6205  113.6205  113.5395  113.4991 113.5395  113.6205  113.6609'.split()
    for x in x_list:
        s = [float(x),0]
        stations.append(s)
    count = 0
    y_list =  '23.5560   23.6027   23.5794   23.5326   23.5028   23.5326   23.5794   23.6261   23.6261   23.5560 23.4859   23.4859'.split()

    for y in y_list:
        stations[count][1] = float(y)
        count += 1

    for st in stations:
        d = {}
        d['lng'] = st[0]
        d['lat'] = st[1]
        d['name'] = 'hello'
        d['icon_uri'] = url_for('static', filename=BASESTATION_IMG_URI)
        data.append(d)
    #
    # for device in devices:
    #     d = {}
    #     d['device_id'] = device.id
    #     d['lng'] = device.lng
    #     d['lat'] = device.lat
    #     d['name'] = device.name
    #     if device.type == NODE:
    #         d['icon_uri'] = url_for('static', filename=NODE_IMG_URI)
    #     else:
    #         d['icon_uri'] = url_for('static', filename=BASESTATION_IMG_URI)
    #     data.append(d)
    return jsonify({'data': data})


if __name__ == '__main__':
    app.run(port=8123)

