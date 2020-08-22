import os
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


@app.teardown_appcontext
def teardown_db(exception):
    db = getattr(g, '_database', None)
    if db is None:
        db.close()


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
        # parser.add_argument('edited_message', required=False)
        # parser.add_argument('channel_post', required=False)
        # parser.add_argument('edited_channel_post', required=False)
        # parser.add_argument('inline_query', required=False)
        # parser.add_argument('chosen_inline_result', required=False)
        # parser.add_argument('callback_query', required=False)
        # parser.add_argument('shipping_query', required=False)
        # parser.add_argument('pre_checkout_query', required=False)
        # parser.add_argument('poll', required=False)
        # parser.add_argument('poll_answer', required=False)

        # Parse the arguments into an object
        args = parser.parse_args()

        app.logger.info("Hello")
        app.logger.info(args)
        # if args['message'].lower() == "/start":
        #     send_message("id", "BOKITA EL MAS GRANDE, PAPA!!!")
        # else:
        #     send_message("id", "No entiendo vieja. Te fuiste a la B")


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
