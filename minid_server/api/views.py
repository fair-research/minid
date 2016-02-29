from flask import jsonify, make_response, request, render_template, abort
from models import *
import uuid
import datetime
from providers import EZIDClient
from app import app, db, minid_email

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
   
    if title is None: 
        title = ""
    #data = {"erc.who" : creator, "erc.what" : title, "erc.when" : str(created)} 
    data= {"_profile" : "datacite", "datacite.creator" : creator, "datacite.title" :  title, 
            "datacite.publicationyear" : str(created.year),
            "datacite.publisher": "BD2K Minid"}#, "datacite.resourcetype" : "dataset"}
   
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
#
# {
#  checksum: xxx
#  location: xxx
#  title: xxx
#  email: xxx
#  code: xxx
#  test: True
# }
@app.route('/minid', methods=['GET', 'POST'])
def create_entity():
    if request.method == 'GET':
        return render_template("index.html")
    
    if not request.json:
        print "Missing checksum in POST %s" % request.json
        abort(400)

    if not 'checksum' in request.json:
        print "Missing checksum and/or user details (email, code)"
        abort(400)

    entity, title, location = None, None, None
    checksum = request.json["checksum"] 
    email = request.json["email"]
    code = request.json["code"]
    title = request.json.get("title")
    location = request.json.get("location")

    test = False
    if "test" in request.json:
        test = request.json["test"]
    created = datetime.datetime.now()
    
    user = Miniduser.query.filter_by(email=email, code=code).first()
    if not user:
        print "User %s with code %s doesn't exist." % (email, code)
        abort(400)

    if test:
        checksum = "%s%s" % (TEST_CHECKSUM_PREFIX, checksum)
    entity = Entity.query.filter_by(checksum=checksum).first()

    if entity:
        print "Entity (%s) exists" % entity.identifier
    else:
        identifier = create_ark(user.name, title, created, test)
        print "Created new identifier %s" % str(identifier)
        if test:
            entity = Entity(user, str(identifier), checksum, created)
        else:
            entity = Entity(user, str(identifier), checksum, created)
        db.session.add(entity)

    # Get existing locations and titles to avoid duplicates
    titles = [t.title for t in entity.titles]
    locations = [l.uri for l in entity.locations]

    if title and title not in titles:
        title = Title(entity, user, title, created)
        db.session.add(title)
    
    if location and location not in locations:
        location = Location(entity, user, location, created)
        db.session.add(location)

    db.session.commit()
    return jsonify({'identifier': entity.identifier}), 201


# Register a new user.. 
# {
#  name: xxx
#  email: xxx
#  orcid: xx
# }
@app.route('/minid/user', methods=['POST','PUT'])
def register_user():
    if not request.json:
        print "Request is not JSON"
        abort(400)

    if not 'name' in request.json or not 'email' in request.json:
        print "Malformed request missing name or email %s" % request.json
        abort(400)
                                            
    email = request.json["email"]
    name = request.json["name"]
    orcid = request.json.get("orcid")

    code = str(uuid.uuid4())

    user = Miniduser.query.filter_by(email=email).first()
    if user is None: 
        user = Miniduser(name, orcid, email, code)
        db.session.add(user)
    else: 
        print "Updating existing user."
        user.name = name
        user.orcid = orcid
        user.code = code

    db.session.commit()
    
    minid_email.send_email(email, code)

    return jsonify(user.get_json()), 201

