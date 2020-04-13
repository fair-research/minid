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
import logging
import json
import traceback
import datetime
import pytz
import tzlocal
from argparse import ArgumentParser

from fair_identifiers_client.identifiers_api import IdentifierClientError

from minid.exc import MinidException, LoginRequired

import minid

SERVICE_DATE_FORMAT = '%Y-%m-%dT%H:%M:%S.%f'
DATE_FORMAT = '%A, %B %d, %Y %H:%M:%S %Z'

cli = ArgumentParser()
subparsers = cli.add_subparsers(dest="subcommand")

cli.add_argument('--quiet', action="store_true", help="suppress output")
cli.add_argument('--verbose', action="store_true", help="detailed output")
cli.add_argument('--json', action="store_true", help="json output")

log = logging.getLogger(__name__)


def execute_command(cli, args, logger):
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    if args.quiet:
        logger.setLevel(logging.CRITICAL)

    subcommand = args.subcommand

    if subcommand is None:
        cli.print_help()
        return

    try:
        ret = args.func(minid.MinidClient(), args)
        # These subcommands all return minids
        if subcommand in ('register', 'update', 'check'):
            if args.json:
                print(json.dumps(ret.data, indent=2))
            else:
                if ret.data.get('identifiers') == []:
                    log.info('No minids found for file.')
                elif ret.data.get('identifiers'):
                    for m in ret.data.get('identifiers'):
                        pretty_print_minid(minid.MinidClient, m)
                        print_separator()
                else:
                    pretty_print_minid(minid.MinidClient, ret.data)
        elif subcommand == 'batch-register':
            print(json.dumps(ret, indent=2))
    except LoginRequired:
        message = 'Authentication required, please login and try again.'
        if args.json:
            print(json.dumps({'error': str(message)}))
        else:
            log.error(message)
    except IdentifierClientError as ice:
        if args.json:
            print(json.dumps(ice.raw_json, indent=2))
        else:
            error = str(ice)
            if ice.raw_json and ice.raw_json.get('message'):
                error = ice.raw_json['message']
            log.error(error)
    except (MinidException, FileNotFoundError) as me:
        if args.json:
            print(json.dumps({'error': str(me)}))
        else:
            log.error(me)
    except Exception:
        log.error('An unexpected error occurred, please file a bug report '
                  'and we will fix this as soon as we can.')
        if args.verbose:
            traceback.print_exc()


def print_separator():
    print('-' * 50)


def print_date(iso_datestring):
    """Pretty print dates in user's local time zone"""
    if not iso_datestring:
        return ''
    dt = datetime.datetime.strptime(iso_datestring, SERVICE_DATE_FORMAT)
    user_tz = pytz.timezone(tzlocal.get_localzone().zone)
    dt_local = user_tz.fromutc(dt)
    return dt_local.strftime(DATE_FORMAT)


def pretty_bytes(size):
    # Credit to: https://stackoverflow.com/a/1094933
    size = int(size)
    for unit in ['bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB']:
        if abs(size) < 1024:
            if unit == 'bytes':
                return '{} {}'.format(size, unit)
            return '{:.1f}{}'.format(size, unit)
        size /= 1024
    return '{:.1f}{}'.format(size, 'YB')


def pretty_print_minid(cli, command_json):
    """Minid specific function to print minid relevant fields to the console
    in a human readable format. Only supports select fields."""
    fields = [
        {
            'title': 'Minid',
            'func': lambda m: cli.to_minid(m['identifier'])
        },
        {
            'title': 'Title',
            'func': lambda m: m['metadata'].get('title')
        },
        {
            'title': 'Checksums',
            'func': lambda m: '\n'.join(['{} ({})'.format(c['value'],
                                                          c['function'])
                                        for c in m['checksums']])
        },
        {
            'title': 'Size',
            'func': lambda m: pretty_bytes(m.get('metadata',
                                                 {}).get('length', 0))
        },
        {
            'title': 'Created',
            'func': lambda m: print_date(m.get('created'))
        },
        {
            'title': 'Updated',
            'func': lambda m: print_date(m.get('updated'))
        },
        {
            'title': 'Landing Page',
            'func': lambda m: m['landing_page']
        },
        {
            'title': 'Locations',
            'func': lambda m: ', '.join(m['location'])
        },
        {
            'title': 'Active',
            'func': lambda m: m.get('active') or 'False'
        },
        {
            'title': 'Replaces',
            'func': lambda m: (cli.to_minid(m['replaces'])
                               if m.get('replaces') else '')
        },
        {
            'title': 'Replaced By',
            'func': lambda m: (cli.to_minid(m['replaced_by'])
                               if m.get('replaced_by') else '')
        }
    ]
    prepped_lines = [(f['title'], f['func'](command_json)) for f in fields]
    output = ['{0:20} {1}'.format('{}:'.format(title), text or '')
              for title, text in prepped_lines]
    output = '\n{}'.format('\n'.join(output))
    print(output)
