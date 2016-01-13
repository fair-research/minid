from flask import jsonify, make_response, request, render_template
from models import *
import uuid
import datetime
from providers import EZIDClient
from app import app, db

# When using the test capabilities we append TEST to the checksum to avoid 
# colusion with the real namespace
TEST_CHECKSUM_PREFIX = "TEST-"

def create_ark(creator, title, created, test):
    print "Creating ARK"
    if test:
        print "Using test EZID namespace"
        client = EZIDClient(app.config["TEST_EZID_SERVER"],
            app.config["TEST_EZID_USERNAME"],
            app.config["TEST_EZID_PASSWORD"],
            app.config["TEST_EZID_SCHEME"],
            app.config["TEST_EZID_SHOULDER"])
    else:
        client = EZIDClient(app.config["EZID_SERVER"], 
            app.config["EZID_USERNAME"], 
            app.config["EZID_PASSWORD"], 
            app.config["EZID_SCHEME"], 
            app.config["EZID_SHOULDER"])
    
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

    test = request.args.get("test") in ["True", "true", "t", "T"]
    print "Getting landing page %s (%s)" % (path, test)
    entity = Entity.query.filter_by(identifier=path).first()
    if entity is None:
        if test:
            entity = Entity.query.filter_by(checksum="%s%s" % (TEST_CHECKSUM_PREFIX, path)).first()
        else:
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
    test = False
    if "test" in request.json:
        test = request.json["test"]
    created = datetime.datetime.now()
    
    user = Miniduser.query.filter_by(name=username).first()
    if not user:
        print "User doesn't exist. Creating %s" % username
        user = Miniduser(username, orcid)
        db.session.add(user)

    if test:
        checksum = "%s%s" % (TEST_CHECKSUM_PREFIX, checksum)
    entity = Entity.query.filter_by(checksum=checksum).first()

    if entity:
        print "Entity (%s) exists" % entity.identifier
    else:
        identifier = create_ark(username, request.json['title'], str(created), test)
        print "Created new identifier %s" % str(identifier)
        if test:
            entity = Entity(user, str(identifier), checksum, created)
        else:
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

