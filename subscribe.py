#!/usr/bin/python
# -*- coding: utf-8 -*-

import paho.mqtt.subscribe as subscribe
from marshmallow import ValidationError
from tinydb import where

from common import db
from schemas import VitalsSchema

topics = ['/vitalerter/adrian/vitals']


# Extract a vitals data message from MQ and update vitals data in the database
def callback(client, userdata, message):
    # Simply print it out rather than logging
    print("Got a message on topic %s: %s" % (message.topic, message.payload))

    table = db.table("devices")

    fields = message.payload.decode("utf-8").split(",")
    if len(fields) != 3:
        print("Invalid message format")
        return

    device_id = int(fields[0])
    HR = int(fields[1])
    RR = int(fields[2])

    devices = table.search(where("device_id") == device_id)
    if len(devices) == 0:
        print("Invalid device ID")
        return
    vitals = devices[0]["vitals"]
    # Set vitals data
    vitals["current"]["HR"] = HR
    vitals["current"]["RR"] = RR
    vitals["buffer"]["HR"].append(HR)
    vitals["buffer"]["HR"] = vitals["buffer"]["HR"][-100:]
    vitals["buffer"]["RR"].append(RR)
    vitals["buffer"]["RR"] = vitals["buffer"]["RR"][-100:]
    try:
        # Validate
        VitalsSchema().load(vitals)
    except ValidationError as err:
        print("Validation error: %s" % str(err.messages))
        return
    except Exception as err:
        print("Unknown error: %s" % str(err))
        return

    # Update
    result = table.update({"vitals": vitals}, where("device_id") == device_id)
    if len(result) > 0:
        print("Updated vitals data (HR: %d, RR: %d) on device %d successfully!" % (HR, RR, device_id))


if __name__ == '__main__':
    subscribe.callback(callback, topics, hostname="broker.hivemq.com")
