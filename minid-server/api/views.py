from flask import jsonify, make_response, request, render_template
from models import *
import uuid
import datetime
from providers import EZIDClient
from app import app, db

def create_ark(creator, created, title):
    print "Creating ARK"
    client = EZIDClient()
    data = {"erc.who" : creator, "erc.what" : title, "erc.when" : created }

    response = client.mint_identifier(data)
    print "minted %s" % app.config["HOSTNAME"] 
    data ["_target"] = "%s/%s" % (app.config["LANDING_PAGE"], response["identifier"])
    client.update_identifier(response["identifier"], data)
    return response["identifier"]

def request_wants_json():
    best = request.accept_mimetypes \
        .best_match(['application/json', 'text/html'])
    return best == 'application/json' and \
        request.accept_mimetypes[best] > \
        request.accept_mimetypes['text/html']

@app.route('/minid/landingpage/<path:path>', methods=['GET'])
def get_entity(path):
    print "Getting landing page %s" % path
    entity = Entity.query.filter_by(identifier=path).first()
    if entity is None: 
        entity = Entity.query.filter_by(checksum=path).first()
    if entity is None: 
        return "Could not locate entity %s" % path, 404
    if request_wants_json():
        return jsonify(entity.get_json())
    else:
        return render_template("entity.html", data=entity.get_json())

@app.route('/minid', methods=['GET', 'POST'])
def create_entity():
    if request.method == 'GET':
        return render_template("index.html")
    
    if not request.json or not 'checksum' in request.json:
        print "Missing checksum in POST %s" % request.json
        abort(400)
    entity, title, location, orcid = None, None, None, None
    checksum = request.json["checksum"] 
    username = request.json["username"]
    orcid = request.json["orcid"]
    created = datetime.datetime.now()
    
    user = Miniduser.query.filter_by(name=username).first()
    if not user:
        print "User doesn't exist. Creating %s" % username
        user = Miniduser(username, orcid)
        db.session.add(user)

    entity = Entity.query.filter_by(checksum=checksum).first()

    if entity:
        print "Entity (%s) exists" % entity.identifier
    else:
        identifier = create_ark(username, request.json['title'], str(created))
        print "Created new identifier %s" % str(identifier)
        entity = Entity(user, str(identifier), checksum, created)
        db.session.add(entity)

    if 'title' in request.json:
        title = Title(entity, user, request.json['title'], created)
        db.session.add(title)
    locations = [l.uri for l in entity.locations]
    
    if 'location' in request.json and request.json['location'] not in locations:
        location = Location(entity, user, request.json['location'], created)
        db.session.add(location)

    db.session.commit()
    return jsonify({'identifier': entity.identifier}), 201

