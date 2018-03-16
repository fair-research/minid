#!/usr/bin/python

from argparse import ArgumentParser
import os
import json
import minid_client.minid_client_api as mca
from minid_client import __VERSION__
# Usage 
# minid.py <file_path> --- will give you info on file if it has been registered
# minid.py <identifer> -- will give you info on identifier
# minid.py <file_path> --register --title "My file"
# minid.py <identifier> --update --title "My file" --locations "globus://file" "http://file" --status "TOMBSTONE" --obsoleted_by "ark://99999/abcd"
# minid.py --register_user --email "Email" --name "Name" [--orcid "orcid"]


def parse_cli():
    description = 'BD2K minid tool for assigning an identifier to data'
    parser = ArgumentParser(description=description)
    parser.add_argument('--register', action="store_true", help="Register the file")
    parser.add_argument('--batch-register', action="store_true", help="Register multiple files listed in a JSON manifest")
    parser.add_argument('--update', action="store_true", help="Update a minid")
    parser.add_argument('--test', action="store_true", default=False, help="Run a test of this registration using the test minid namespace")
    parser.add_argument('--json', action="store_true", help="Return output as JSON")
    parser.add_argument('--server', help="Minid server")
    parser.add_argument('--title', help="Title of named file")
    parser.add_argument('--locations',  nargs='+', help="Locations for accesing the file")
    parser.add_argument('--status', help="Status of the minid (ACTIVE or TOMBSTONE)")
    parser.add_argument('--obsoleted_by', help="A minid that replaces this minid")
    parser.add_argument("--content_key", help="A key that can be uesd to compare equivalent content")
    parser.add_argument('--config', default=mca.DEFAULT_CONFIG_FILE)
    parser.add_argument('--register_user', action="store_true", help="Register a new user")
    parser.add_argument('--email', help="User email address")
    parser.add_argument('--name', help="User name")
    parser.add_argument('--orcid', help="user orcid")
    parser.add_argument('--code', help="user code")
    parser.add_argument('--globus_auth_token',
                        help='A valid user Globus Auth token instead of a code',
                        default=None)
    parser.add_argument('--quiet', action="store_true", help="suppress logging output")
    parser.add_argument('--version', action='version', version=__VERSION__)
    parser.add_argument('filename', nargs="?", help="file or identifier to retrieve information about or register")

    return parser.parse_args()


def _main():
    args = parse_cli()
    if not args.quiet:
        mca.configure_logging()

    config = mca.parse_config(args.config)

    server = config["minid_server"]
    if args.server:
        server = args.server

    entities = None

    # register a new user
    if args.register_user:
        mca.register_user(server, args.email, args.name, args.orcid,
                          args.globus_auth_token)
        return

    # if we got this far we *must* have a filename (or identifier) arg
    if not args.filename:
        print("Either a file name or an identifier must be specified.")
        return

    if args.batch_register:
        results = mca.register_entities(server,
                                        args.email if args.email else config["email"],
                                        args.code if args.code else config["code"],
                                        args.filename,
                                        args.test,
                                        args.content_key,
                                        args.globus_auth_token)
        print(json.dumps(results, indent=2))
        return

    # see if this file or name exists
    file_exists = os.path.isfile(args.filename)
    if file_exists:
        checksum = mca.compute_checksum(args.filename)
        checksum_function = "SHA256"
        entities = mca.get_entities(server, checksum, args.test)
    else:
        entities = mca.get_entities(server, args.filename, args.test)
        if not entities:
            print("No entity registered with identifier: %s" % args.filename)
            return
   
    # register file or display info about the entity
    if args.register:
        if entities and not file_exists:
            print("You must use the --update command to update a minid")
            return
        else:
            locations = args.locations
            if locations is None or len(locations) == 0:
                if "local_server" in config:
                    locations = ["%s%s" % (config["local_server"], os.path.abspath(args.filename))]
            mca.register_entity(server,
                                checksum,
                                args.email if args.email else config["email"],
                                args.code if args.code else config["code"],
                                locations, args.title, args.test, args.content_key,
                                args.globus_auth_token, checksum_function)
    elif args.update:
        if not entities:
            print("No entity found to update. You must use a valid minid.")
            return
        elif len(entities) > 1:
            print("More than one minid identified. Please use a minid identifier")
        else:
            entity = list(entities.values())[0]
            if args.status:
                entity['status'] = args.status
            if args.obsoleted_by:
                entity['obsoleted_by'] = args.obsoleted_by
            if args.title:
                entity['titles'] = [{"title": args.title}]
            if args.locations:
                locs = []
                for l in args.locations:
                    locs.append({'uri': l})
                entity['locations'] = locs

            updated_entity = mca.update_entity(server,
                                               args.filename,
                                               entity,
                                               args.email if args.email else config["email"],
                                               args.code if args.code else config["code"],
                                               args.globus_auth_token)
            print(updated_entity)
    else:
        if entities:
            mca.print_entities(entities, args.json)
        else:
            print("File is not named. Use --register to create a name for this file.")


def main():
    try:
        _main()
    except mca.MinidAPIException:
        pass


if __name__ == '__main__':
    main()
