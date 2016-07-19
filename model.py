from extenction import db
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.exc import IntegrityError
from config import BASESTATION
from sqlalchemy import desc


class Device(db.Model):
    __tablename__ = 'devices'
    id = db.Column(db.Integer, primary_key=True)
    lng = db.Column(db.Float)
    lat = db.Column(db.Float)
    type = db.Column(db.Integer(), nullable=False, default=2)          # 1: base station   2: node
    name = db.Column(db.String(32))
    eui = db.Column(db.String(32), nullable=False)

    @classmethod
    def get_devices(cls):
        return cls.query.all()

    @classmethod
    def get_four_base_stations(cls):
        return cls.query.limit(4).all()

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


class PositionRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    create_time = db.Column(db.DateTime, nullable=False)
    lng = db.Column(db.Float, nullable=False)
    lat = db.Column(db.Float, nullable=False)
    eui = db.Column(db.CHAR(32), nullable=False)

    @classmethod
    def get_records(cls, eui, count):
        return cls.query.filter(cls.eui == eui).order_by(desc(cls.create_time)).limit(count).all()