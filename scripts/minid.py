#!/usr/bin/python

from argparse import ArgumentParser 
from ConfigParser import ConfigParser
import hashlib
import os
import requests
import json

# Usage 
# minid.py <file_path> --- will give you info on file if it has been registered
# minid.py <identifer> -- will give you info on identifier
# minid.py <file_path> --register --title "My file"
# minid.py --register_user --email "Email" --name "Name" [--orcid "orcid"]

def parse_cli():
    description = 'BD2K minid tool for assigning an identifier to data'
    parser = ArgumentParser(description=description)
    parser.add_argument('--register', action="store_true", help="Register the file")
    parser.add_argument('--test', action="store_true", help="Run a test of this registration using the test minid namespace")
    parser.add_argument('--json', action="store_true", help="Return output as JSON")
    parser.add_argument('--server', help="Minid server")
    parser.add_argument('--title', help="Title of named file")
    parser.add_argument('--url', help="Accessible URL of named file")
    parser.add_argument('--config', default='%s/.minid/minid-config.cfg' %  os.path.expanduser('~'))
    parser.add_argument('--register_user', action="store_true", help="Register a new user")
    parser.add_argument('--email', help="User email address")
    parser.add_argument('--name', help="User name")
    parser.add_argument('--orcid', help="user orcid")
    parser.add_argument('--code', help="user code")
    parser.add_argument('filename', nargs="?", help="file or identifier to retrieve information about or register")

    return parser.parse_args()

def parse_config(config_file):
    config = ConfigParser()
    config.read(config_file)
    return dict(config.items('general'))

def compute_checksum(open_file, algorithm, block_size=65536):
    buf = open_file.read(block_size)
    while len(buf) > 0:
        algorithm.update(buf)
        buf = open_file.read(block_size)
    return algorithm.hexdigest()

def get_entity(server, name, test):
    query = ""
    if test:
        query = "?test=true"
    r = requests.get("%s/landingpage/%s%s" % (server, name, query), headers={"Accept" : "application/json"})
    if r.status_code == 404:
        return None
    return r.json()

def create_entity(server, entity):
    print "Creating entity %s" % entity
    r = requests.post(server, json=entity, headers={"Accept" : "application/json"})
    if r.status_code in [200, 201]:
        return r.json()
    else: 
        print "Error creating entity (%s)" % r.status_code

def entity_json(email, code, checksum, file_path, title, test):
    entity = {"email" :  email, "code": code, "checksum": checksum}
    if test:
        entity ["test"] = test
    if file_path:
        entity["location"] = file_path
    if title: 
        entity["title"] = title
    return entity

def print_entity(entity, json):
    if json:
        print entity
    else:
        print "Identifier: %s" % entity["identifier"]
        print "Created by: %s (%s)" % (entity["creator"], entity["orcid"])
        print "Created: %s" % entity["created"]
        print "Checksum: %s" % entity["checksum"]
        print "Locations:"
        for l in entity["locations"]:
            print "  %s - %s" % (l["creator"], l["uri"])
        print "Title:"
        for t in entity["titles"]:
            print "  %s - %s" % (t["creator"], t["title"])

def register_user(server, email, name, orcid):
    user = {"name" : name, "email" : email}
    if orcid:
        user["orcid"] = orcid
    r = requests.post("%s/user" % server, json=user, headers={"Content-Type" : "application/json"})
    return r.json()

def register_entity(server, entity, file_path, checksum, args, config):
    if entity:
        print "Appending to registered entity %s" % entity["identifier"]
    else: 
        print "Creating new name"
    
    accessible_path = ""
    if args.url:
        accessible_path = args.url
    else:
        if "local_server" in config:
            accessible_path = "%s%s" % (config["local_server"], file_path)
    
    if args.email and args.code:
        email = args.email
        code = args.code
    else:
        email = config["email"]
        code = config["code"]

    result = create_entity(server, entity_json(email, code, checksum, accessible_path, args.title, args.test))
    if result:
        print "Created new minid: %s" % result["identifier"]

def main():
    args = parse_cli()
    config = parse_config(args.config)

    server = config["minid_server"]
    if args.server:
        server = args.server
    
    # register a new user
    if args.register_user:
        register_user(server, args.email, args.name, args.orcid)
        return

    entity, checksum, file_path = None, None, None
   
    # see if tihs file or name exists
    if os.path.exists(args.filename):
        file_path = os.path.abspath(args.filename)
        open_file = open(args.filename)
        checksum = compute_checksum(open_file, hashlib.sha256())
        entity = get_entity(server, checksum, args.test)
    else: 
        entity = get_entity(server, args.filename, False)
        if entity is None: 
            print "No file registered with name %s" % args.filename
            return
        checksum = entity["checksum"]
   
    # register or display info about the entity
    if args.register:
        register_entity(server, entity, file_path, checksum, args, config)
    else:
        if entity:
            print_entity(entity, args.json)
        else:
            print "File is not named. Use --register to create a name for this file."

if __name__ == '__main__':
    main()
