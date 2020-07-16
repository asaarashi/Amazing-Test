# Amazing Test
An amazing test.

## Requirements
* Python 3.6
* Flask (For installing Flask and virtual env, please refer to https://flask.palletsprojects.com/en/1.1.x/installation/)
* Write permission for the project directory (for storing database file)

## Installation and run
In the project directory, you can run:

Enter the virtual environment,
#### `. venv/bin/activate`
And then install dependencies,
#### `pip install -r requirements.txt`

### Start the API server
Execute the following command to run the app:
#### `flask run`
Open [http://localhost:5000](http://localhost:5000) in the browser, if it displays "Hello world!", the server is ready.
### Publish and subscribe via MQTT
Startup the subscriber process,
#### `python subscribe.py`
And then open another terminal to publish a row of test data, 
#### `python publish_test_data.py`

## Powered by 
* Flask
* marshmallow
* flask-marshmallow
* TinyDB
