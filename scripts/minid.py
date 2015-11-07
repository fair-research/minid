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

def parse_cli():
    description = 'BD2K minid tool for assigning an identifier to data'
    parser = ArgumentParser(description=description)
    parser.add_argument('name', help="file or identifier to retrieve information about or register")
    parser.add_argument('--register', action="store_true", help="Register the file")
    parser.add_argument('--json', action="store_true", help="Return output as JSON")
    parser.add_argument('--title', help="Title of named file")
    parser.add_argument('--config', default='%s/.minid/minid-config.cfg' %  os.path.expanduser('~'))
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

def get_entity(server, name):
    r = requests.get("%s/landingpage/%s" % (server, name), headers={"Accept" : "application/json"})
    if r.status_code == 404:
        return None
    return r.json()

def create_entity(server, entity):
    r = requests.post(server, json=entity, headers={"Accept" : "application/json"})
    return r.json()

def entity_json(username, orcid, checksum, file_path, title):
    entity = {"username" :  username, "orcid": orcid, "checksum": checksum}
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

def main():
    args = parse_cli()
    config = parse_config(args.config) 
    entity, checksum, file_path, orcid = None, None, None, None
    title = args.title 
    server = config["minid_server"]
    local_server = "" 
    if "local_server" in config: 
        local_server = config["local_server"]
    if "orcid" in config:
        orcid = config["orcid"]

    username = config["username"]
   
    if os.path.exists(args.name):
        file_path = os.path.abspath(args.name)
        open_file = open(args.name)
        checksum = compute_checksum(open_file, hashlib.sha256())
        entity = get_entity(server, checksum)
    else: 
        entity = get_entity(server, args.name)
        if entity is None: 
            print "No file registered with name %s" % args.name
            return
        checksum = entity["checksum"]

    if args.register:
        if entity:
            print "Appending to registered entity %s" % entity["identifier"]
        else: 
            print "Creating new name"
        result = create_entity(server, entity_json(username, orcid, checksum, "%s%s" % (local_server, file_path), title))
        if result: 
            print "Created new minid: %s" % result["identifier"]
    else:
        if entity:
            print_entity(entity, args.json)
        else:
            print "File is not named. Use --register to create a name for this file."

if __name__ == '__main__':
    main()
