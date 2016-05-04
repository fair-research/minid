#!/usr/bin/python

from argparse import ArgumentParser 
from minid_server.providers import ezid

# Usage 


def parse_cli():
    description = 'Update registered identity'
    parser = ArgumentParser(description=description)
    parser.add_argument('--identifier')
    parser.add_argument('--target')
    parser.add_argument('--server', default='https://ezid.cdlib.org')
    parser.add_argument('--username')
    parser.add_argument('--password')
    return parser.parse_args()


def main():
    args = parse_cli()
    client = ezid.EZIDClient(args.server, args.username, args.password, None, None)
    
    data = {'_target': args.target}

    client.update_identifier(args.identifier, data)


if __name__ == '__main__':
    main()
