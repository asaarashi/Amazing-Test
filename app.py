from flask import request, jsonify
from marshmallow import ValidationError
from schemas import PatientSchema, DeviceSchema, AssignDeviceSchema
from common import app, db
from tinydb import where


def build_entities_data(rows, key):
    data = {}
    for row in rows:
        try:
            data[row[key]] = row
        except KeyError:
            pass

    return data


@app.route('/')
def hello_world():
    return 'Hello, World!'


# Create a patient
@app.route('/patient', methods=['POST'])
def create_patient():
    if not request.json:
        return jsonify({'status': 400}), 400

    try:
        table_patients = db.table("patients")
        # Validation by using marshmallow
        data = PatientSchema().load(request.json)
        if len(table_patients.search(where("patient_id") == request.json["patient_id"])) > 0:
            raise ValidationError(field_name="patient_id", message="The patient ID already exists")

        table_patients.insert(data)

        return jsonify({'status': 201}), 201
    except ValidationError as err:
        return jsonify({'status': 422, 'message': err.messages}), 422


# Get a patient
@app.route('/patient', methods=['GET'])
def get_patient():
    if not request.json:
        return jsonify({'status': 400}), 400

    table_patients = db.table("patients")
    patients = table_patients.search(where("patient_id") == request.json["patient_id"])
    if len(patients) == 0:
        return jsonify({'status': 404}), 404

    return jsonify(build_entities_data(patients, 'patient_id')), 200


# Create a device
@app.route('/device', methods=['POST'])
def create_device():
    if not request.json:
        return jsonify({'status': 400}), 400

    try:
        # Validation by using marshmallow
        data = DeviceSchema().load(request.json)
        table_devices = db.table("devices")
        if len(table_devices.search(where("device_id") == request.json["device_id"])) > 0:
            raise ValidationError(field_name="device_id", message="The device ID already exists")

        table_devices.insert(data)

        return jsonify({'status': 201}), 201
    except ValidationError as err:
        return jsonify({'status': 422, 'message': err.messages}), 422


# Get a device
@app.route('/device', methods=['GET'])
def get_device():
    if not request.json:
        return jsonify({'status': 400}), 400

    table_devices = db.table("devices")
    devices = table_devices.search(where("device_id") == request.json["device_id"])
    if len(devices) == 0:
        return jsonify({'status': 404}), 404

    return jsonify(build_entities_data(devices, 'device_id')), 200


# Assign a device
@app.route('/patient/assign_device', methods=['POST'])
def assign_device():
    if not request.json:
        return jsonify({'status': 400}), 400

    try:
        data = AssignDeviceSchema().load(request.json)
    except ValidationError as err:
        return jsonify({'status': 422, 'message': err.messages}), 422

    table_devices = db.table("devices")
    devices = table_devices.search(where("device_id") == data["device_id"])
    if len(devices) == 0:
        return jsonify({'status': 404}), 404

    # Find the patient and update its field device_id
    table_patients = db.table("patients")
    patients = table_patients.search(where("patient_id") == data["patient_id"])
    if len(patients) == 0:
        return jsonify({'status': 404}), 404

    table_patients.update({"device_id": devices[0]["device_id"]}, where("patient_id") == patients[0]["patient_id"])

    return jsonify({'status': 200}), 200


# Get assigned devices
@app.route('/patient/assign_device', methods=['GET'])
def get_assigned_device():
    if not request.json:
        return jsonify({'status': 400}), 400

    table_patients = db.table("patients")
    patients = table_patients.search(where("patient_id") == request.json["patient_id"])
    if len(patients) == 0:
        return jsonify({'status': 404}), 404
    patient = patients[0]

    table_devices = db.table("devices")
    devices = []
    if 'device_id' in patient:
        devices = table_devices.search(where("device_id") == patient['device_id'])

    return jsonify(build_entities_data(devices, 'device_id')), 200


# Get patients summary
@app.route('/patients/status', methods=['GET'])
def patients_status():
    table_patients = db.table("patients")
    if not request.json or "only_with_devices" not in request.json:
        patients = table_patients.all()
    else:
        patients = table_patients.search(where("device_id") > -1)
    table_devices = db.table("devices")

    def avg(lst):
        try:
            return round(sum(lst) / len(lst), 2)
        except ZeroDivisionError:
            return 0

    data = []
    for patient in patients:
        row = patient
        if "device_id" in patient:
            devices = table_devices.search(where("device_id") == patient["device_id"])
            if len(devices) > 0:
                device = devices[0]
                device_summary = {"device_id": device["device_id"],
                                  "vitals": {"current": device["vitals"]["current"],
                                             "avg": {"HR": avg(device["vitals"]["buffer"]["HR"]),
                                                     "RR": avg(device["vitals"]["buffer"]["RR"])}}}

                row = {**row, **device_summary}

        data.append(row)
    return jsonify(data), 200
