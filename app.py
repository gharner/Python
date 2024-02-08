from firebase_admin import credentials
from firebase_admin import firestore
from flask import Flask, render_template, jsonify
from flask_cors import CORS
import firebase_admin
import json
import os
import requests

cred = credentials.Certificate('static/gregharner-84eb9.json')
firebase_admin.initialize_app(cred)
db = firestore.client()
app = Flask(__name__)

CORS(app)

@app.route("/v1/station", methods=["GET"])
def space_station():
    station =requests.get(url="http://api.open-notify.org/iss-now.json").json()    
    return station

@app.route("/v1/cities", methods=["GET"])
def get_cities():
    docs = db.collection("cities").stream()
    cities = []
    for doc in docs:
        # Convert each DocumentSnapshot to a dictionary
        city = doc.to_dict()
        city["id"] = doc.id  # Optionally, add the document ID
        cities.append(city)
    return jsonify(cities)  # Return the list of city dictionaries

@app.route("/", methods=["GET"])
def list_routes():
    routes = []
    for rule in app.url_map.iter_rules():
        methods = ','.join(rule.methods)
        routes.append({'endpoint': rule.endpoint, 'methods': methods, 'url': str(rule)})
    return routes

def stringy_pretty(obj, description):
    class CircularReferenceEncoder(json.JSONEncoder):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.seen = set()

        def default(self, o):
            if isinstance(o, (dict, list, tuple, set)):
                if id(o) in self.seen:
                    # Circular reference detected, can return a placeholder or None
                    return None
                self.seen.add(id(o))
            return super().default(o)

    # Serialize the object with circular reference checks
    serialized = json.dumps(obj, cls=CircularReferenceEncoder)

    # Pretty-print the JSON
    pretty_printed = json.dumps(json.loads(serialized), indent=4)

    return render_template("pretty.html", pretty_printed=pretty_printed, description=description)

if __name__ == '__main__':
    server_port = os.environ.get('PORT', '8080')
    app.run(debug=False, port=server_port, host='0.0.0.0') 
  