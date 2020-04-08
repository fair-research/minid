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

from minid.commands.cli import subparsers
from minid.commands.argparse_ext import subcommand, argument, shared_argument
from minid.exc import MinidException

log = logging.getLogger(__name__)

CREATE_UPDATE_ARGS = {
    '--title': {
        'help': 'Title for the minid. Defaults to filename'
    },
    '--locations': {
        'nargs': '+',
        'help': 'Remotely accessible location(s) for the file'
    },
    '--test': {
        'action': 'store_true',
        'default': False,
        'help': 'Register non-permanent Minid in a "test" namespace.'
    },
    '--replaces': {
        'help': 'This Minid replaces another Minid'
    },
}


@subcommand(
    [
        shared_argument('--title'),
        shared_argument('--locations'),
        shared_argument('--test'),
        shared_argument('--replaces'),
        argument(
            "filename",
            help='File to register'
        ),
    ],
    parent=subparsers,
    shared_arguments=CREATE_UPDATE_ARGS,
    help='Register a new Minid',
)
def register(minid_client, args):
    kwargs = dict()
    if args.replaces:
        kwargs['replaces'] = args.replaces
    return minid_client.register_file(
        args.filename,
        title=args.title,
        locations=args.locations,
        test=args.test,
        **kwargs
    )


@subcommand(
    [
        shared_argument('--test'),
        argument(
            'filename',
            help='File to register'
        ),
    ],
    parent=subparsers,
    shared_arguments=CREATE_UPDATE_ARGS,
    help='Register a batch of minids from a file or file stream',
)
def batch_register(minid_client, args):
    return minid_client.batch_register(args.filename, args.test)


@subcommand([
        shared_argument('--title'),
        shared_argument('--locations'),
        argument('--set-active', action='store_true',
                 help='Set minid active.'),
        argument('--set-inactive', action='store_true',
                 help='Set minid inactive'),
        argument('--replaced-by'),
        shared_argument('--replaces'),
        argument(
            "minid",
            help='Minid to update'
        ),
    ],
    parent=subparsers,
    shared_arguments=CREATE_UPDATE_ARGS,
    help='Update an existing Minid'
)
def update(minid_client, args):
    kwargs = dict()
    if args.set_active and args.set_inactive:
        raise MinidException('Cannot use both --set-active and --set-inactive')
    if args.set_active or args.set_inactive:
        kwargs['active'] = True if args.set_active else False
    # Include other kwargs, but only if they have been set by the user.
    for arg in [args.replaces, args.replaced_by]:
        if arg:
            kwargs[arg.__name__] = arg
    return minid_client.update(args.minid, title=args.title,
                               locations=args.locations, **kwargs)


@subcommand(
    [
        argument(
            "entity",
            help='A Minid or local file'),
        argument(
            "--function",
            required=False,
            help='function used to generate the checksum, if provided',
            default='sha256',
        )
    ],
    parent=subparsers,
    help='Lookup a minid or check if a given file has been registered',
)
def check(minid_client, args):
    return minid_client.check(args.entity, args.function)
