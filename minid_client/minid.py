#!/usr/bin/python

from argparse import ArgumentParser
import os
from minid_client import minid_client_api as minid_client

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
    parser.add_argument('--config', default=minid_client.DEFAULT_CONFIG_FILE)
    parser.add_argument('--register_user', action="store_true", help="Register a new user")
    parser.add_argument('--email', help="User email address")
    parser.add_argument('--name', help="User name")
    parser.add_argument('--orcid', help="user orcid")
    parser.add_argument('--code', help="user code")
    parser.add_argument('--quiet', action="store_true", help="suppress logging output")
    parser.add_argument('filename', nargs="?", help="file or identifier to retrieve information about or register")

    return parser.parse_args()


def main():
    args = parse_cli()
    if not args.quiet:
        minid_client.configure_logging()

    config = minid_client.parse_config(args.config)

    server = config["minid_server"]
    if args.server:
        server = args.server
    
    # register a new user
    if args.register_user:
        minid_client.register_user(server, args.email, args.name, args.orcid)
        return

    # if we got this far we *must* have a filename (or identifier) arg
    if not args.filename:
        print("Either a file name or an identifier must be specified.")
        return

    # see if this file or name exists
    file_exists = os.path.isfile(args.filename)
    if file_exists:
        checksum = minid_client.compute_checksum(args.filename)
        entity = minid_client.get_entity(server, checksum, args.test)
    else:
        entity = minid_client.get_entity(server, args.filename, False)
        if entity is None: 
            print("No entity registered with identifier: %s" % args.filename)
            return
        checksum = entity["checksum"]
   
    # register file or display info about the entity
    if args.register:
        if not file_exists:
            print("Only local files can be registered")
            return
        else:
            minid_client.register_entity(server, entity, checksum,
                                         args.email if args.email else config["email"],
                                         args.code if args.code else config["code"],
                                         args.url, args.title, args.test)
    else:
        if entity:
            minid_client.print_entity(entity, args.json)
        else:
            print("File is not named. Use --register to create a name for this file.")

if __name__ == '__main__':
    main()
