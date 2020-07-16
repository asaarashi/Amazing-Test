from flask import Flask
from tinydb import TinyDB
from tinydb_serialization import SerializationMiddleware

from datetime import datetime
from tinydb_serialization import Serializer

# Flask application
app = Flask("Amazing Test")


# Database connection. Using TinyDB https://github.com/msiemens/tinydb.
class DateTimeSerializer(Serializer):
    OBJ_CLASS = datetime  # The class this serializer handles

    def encode(self, obj):
        return obj.strftime('%Y-%m-%dT%H:%M:%S')

    def decode(self, s):
        return datetime.strptime(s, '%Y-%m-%dT%H:%M:%S')


serialization = SerializationMiddleware()
serialization.register_serializer(DateTimeSerializer(), 'TinyDate')
db = TinyDB('db.json', storage=serialization)

# MQTT
topics = ['/vitalerter/adrian/vitals']
hostname = "broker.hivemq.com"
client_id = "adrian8Kj3D"
