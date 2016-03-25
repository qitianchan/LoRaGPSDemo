from flask import Flask, render_template, redirect, url_for, jsonify, request
from config import DefaultConfig
from model import Device
from flask_sqlalchemy import SQLAlchemy
from extenction import db
from config import NODE, BASESTATION, NODE_IMG_URI, BASESTATION_IMG_URI
from flask_wtf import Form
from wtforms.fields import StringField, TextAreaField, SelectField, FloatField, IntegerField
from simulate import get_position

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
        four_node_data = list()
        res = None
        for node in request.form:
            device_id = int(node.rsplit('_')[1])
            device = Device.get(device_id)
            if device:
                lng = device.lng
                lat = device.lat
                t = float(request.form[node])
                data = (lng, lat, t)
                four_node_data.append(data)

        if len(four_node_data) >= 4:
            res = get_position(four_node_data)

        return jsonify({'lng': res[0], 'lat': res[1]})

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
    for device in devices:
        d = {}
        d['device_id'] = device.id
        d['lng'] = device.lng
        d['lat'] = device.lat
        d['name'] = device.name
        if device.type == NODE:
            d['icon_uri'] = url_for('static', filename=NODE_IMG_URI)
        else:
            d['icon_uri'] = url_for('static', filename=BASESTATION_IMG_URI)
        data.append(d)
    return jsonify({'data': data})


if __name__ == '__main__':
    app.run(port=8123)

