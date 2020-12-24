import json
import os
import re
import shelve
import markdown
import requests

# Import the framework
from flask import Flask, g
from flask_restful import Resource, Api, reqparse

# Url and token for telegram messages
API_TOKEN = "1349962959:AAEXec9Yf_H5C_DagKibiGTKk4SOl1QsHN8"
url = "https://api.telegram.org/bot%s/" % API_TOKEN

# Create an instance of Flask
app = Flask(__name__)

# Create the API
api = Api(app)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = shelve.open('bokita.db')
    return db

@app.route("/")
def index():
    """Present some documentation"""

    # Open README
    with open(os.path.dirname(app.root_path) + '/README.md', 'r') as markdown_file:
        # Read the content of the file
        content = markdown_file.read()

        # Convert to HTML
        return markdown.markdown(content)


# Send message
def send_message(chat_id, message):
    params = {"chat_id": chat_id, "text": message}
    response = requests.post(url + "sendMessage", data=params)
    return response


class Webhook(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('update_id', required=True)
        parser.add_argument('message', required=False)

        # Parse the arguments into an object
        args = parser.parse_args()
        app.logger.info("Data received: ")
        app.logger.info(args)

        # The message received is a string containing a pseudo json:
        #   - The attributes are enclosed with ' instead of "
        #   - The boolean values are in python syntax: False instead of false
        msg = args["message"]
        fixed_json = re.sub(r"[“|”|‛|’|‘|`|´|″|′|']", '"', msg)
        fixed_json = re.sub(r"(?is)False", 'false', fixed_json)
        fixed_json = re.sub(r"(?is)True", 'true', fixed_json)
        message = json.loads(fixed_json)

        # Respond to the message received
        if message["text"].lower() == "/start":
            app.logger.info("Sending start msg")
            send_message(message['chat']['id'], "BOKITA, EL MAS GRANDE, PAPA!!!")
            app.logger.info("Message sent")
        elif message["text"].lower() == "/meme":
            app.logger.info("Sending meme")
            send_message(message['chat']['id'], "Proximamente memes")
            app.logger.info("Meme sent")
        else:
            app.logger.info("Sending in construction msg")
            send_message(message['chat']['id'], "Todavía estoy en desarrollo así que no sé contestarte, pero proximamente podré abastecerte de memes, fotos, historia, data de partidos, trivia y más. Riber te fuiste a la B")
            app.logger.info("Message sent")


class DeviceList(Resource):
    def get(self):
        shelf = get_db()
        keys = list(shelf.keys())
        devices = []
        for key in keys:
            devices.append(shelf[key])

        return {'message': 'Success', 'data': devices}, 200

    def post(self):
        parser = reqparse.RequestParser()

        parser.add_argument('identifier', required=True)
        parser.add_argument('name', required=True)
        parser.add_argument('device_type', required=True)
        parser.add_argument('controller_gateway', required=True)

        # Parse the arguments into an object
        args = parser.parse_args()

        shelf = get_db()
        shelf[args['identifier']] = args

        return {'message': 'Device registered', 'data': args}, 201


class Device(Resource):
    def get(self, identifier):
        shelf = get_db()

        # If the key does not exist in the data store, return a 404 error.
        if not (identifier in shelf):
            return {'message': 'Device not found', 'data': {}}, 404

        return {'message': 'Device found', 'data': shelf[identifier]}, 200

    def delete(self, identifier):
        shelf = get_db()

        # If the key does not exist in the data store, return a 404 error.
        if not (identifier in shelf):
            return {'message': 'Device not found', 'data': {}}, 404

        del shelf[identifier]
        return '', 204


api.add_resource(DeviceList, '/devices')
api.add_resource(Device, '/device/<string:identifier>')
api.add_resource(Webhook, '/update')
