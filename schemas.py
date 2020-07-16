# Using marshmallow(https://marshmallow.readthedocs.io/en/stable/) for building data schemas

import datetime as datetime
from flask_marshmallow import Marshmallow
from marshmallow import fields
from marshmallow.validate import Range

from common import app

ma = Marshmallow(app)


class PatientSchema(ma.Schema):
    patient_id = fields.Int(required=True)
    name = fields.String(required=True)
    datetime = fields.DateTime(missing=datetime.datetime.now())

    class Meta:
        # Fields to expose
        fields = ("patient_id", "name", "datetime", "vitals")


fieldHR = fields.Int(required=True, validate=Range(min=50, max=120))
fieldRR = fields.Int(required=True, validate=Range(min=6, max=30))


class VitalsCurrentSchema(ma.Schema):
    HR = fieldHR
    RR = fieldRR

    class Meta:
        # Fields to expose
        fields = ("HR", "RR")


class VitalsBufferSchema(ma.Schema):
    HR = fields.List(fieldHR)
    RR = fields.List(fieldRR)

    class Meta:
        # Fields to expose
        fields = ("HR", "RR")


class VitalsSchema(ma.Schema):
    current = fields.Nested(VitalsCurrentSchema)
    buffer = fields.Nested(VitalsBufferSchema)

    class Meta:
        # Fields to expose
        fields = ("current", "buffer")


class DeviceSchema(ma.Schema):
    device_id = fields.Int(required=True)
    vitals = fields.Nested(VitalsSchema, missing={"current": {"HR": 0, "RR": 0}, "buffer": {"HR": [], "RR": []}})

    class Meta:
        # Fields to expose
        fields = ("device_id", "vitals")


class AssignDeviceSchema(ma.Schema):
    patient_id = fields.Int(required=True)
    device_id = fields.Int(required=True)
