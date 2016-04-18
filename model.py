from extenction import db
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.exc import IntegrityError
from config import BASESTATION

class Device(db.Model):
    __tablename__ = 'devices'
    id = db.Column(db.Integer, primary_key=True)
    lng = db.Column(db.Float, nullable=False)
    lat = db.Column(db.Float, nullable=False)
    type = db.Column(db.Integer(), nullable=False, default=2)          # 1: base station   2: node
    name = db.Column(db.String(32))

    @classmethod
    def get_devices(cls):
        return cls.query.limit(8).all()

    @classmethod
    def get_base_station(cls):
        return cls.query.filter(Device.type == BASESTATION).limit(8).all()

    def save(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def get(cls, device_id):
        return cls.query.filter(Device.id == device_id).first()

    @classmethod
    def delete(cls, device_id):
        device = cls.query.filter(Device.id == device_id).first()
        db.session.delete(device)
        db.session.commit()
