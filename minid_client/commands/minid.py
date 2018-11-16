"""
Copyright 2016 University of Chicago, University of Southern California

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
from __future__ import print_function
import logging

from minid_client.commands import subparsers
from minid_client.commands.argparse_ext import subcommand, argument
from minid_client.config import config
from minid_client.minid_client_api import MinidClient


log = logging.getLogger(__name__)


@subcommand(
    [
        argument(
            '--title',
            help='Title for the minid. Defaults to filename'),
        argument(
            "--locations",
            nargs='+',
            help='Remotely accessible location(s) for the file'),
        argument(
            "--test",
            action='store_true',
            default=False,
            help='Register non-permanent Minid in a "test" namespace.'
        ),
        argument(
            "filename",
            help='File to register'
        ),
    ],
    parent=subparsers,
    help='Register a new Minid',
)
def register(args):
    cli = MinidClient(config.load_tokens().get('identifiers.globus.org'))
    return cli.register(title=args.title, locations=args.locations,
                        test=args.test, filename=args.filename)


@subcommand([
    argument(
        '--title',
        help='Title for the minid. Defaults to filename'),
    argument(
        "--locations",
        nargs='+',
        help='Remotely accessible location(s) for the file'),
    argument(
        "minid",
        help='Minid to update'
    ),
],
    parent=subparsers,
    help='Update an existing Minid'
)
def update(args):
    cli = MinidClient(config.load_tokens().get('identifiers.globus.org'))
    return cli.update(args.minid, title=args.title, locations=args.locations)


@subcommand(
    [
        argument(
            "entity",
            help='A Minid or local file'),
    ],
    parent=subparsers,
    help='Lookup a minid or check if a given file has been registered',
)
def check(args):
    cli = MinidClient(config.load_tokens().get('identifiers.globus.org'))
    if not args.entity.startswith('ark:/'):
        log.warning('File lookups are not yet supported.')
    return cli.check(args.entity)
