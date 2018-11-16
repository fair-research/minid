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

from minid_client.commands import cli
# Importing the commands loads them into argparse.
from minid_client.commands import auth, minid, misc  # noqa

log = logging.getLogger(__name__)

def main():
    logger = logging.getLogger('minid_client')
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.INFO)

    cli.add_argument('--quiet', action="store_true", help="suppress output")
    cli.add_argument('--verbose', action="store_true", help="detailed output")
    cli.add_argument('--json', action="store_true", help="json output")



    args = cli.parse_args()
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    if args.quiet:
        logger.setLevel(logging.CRITICAL)

    subcommand = args.subcommand

    if subcommand is None:
        cli.print_help()
    else:
        try:
            ret = args.func(args)
            # These two don't make API calls:
            #if subcommand not in ('login', 'logout'):
            # These subcommands all return minids
            if subcommand in ('register', 'update', 'check'):
                if args.json:
                    print(json.dumps(ret.data, indent=2))
                else:
                    pretty_print_minid(ret.data)
        except Exception as e:
            log.exception(e)
        # except IdentifierNotLoggedIn as err:
        #     log.info(err)
        #     msg = "Not logged in. Use:\n  identifier login\nto log in."
        #     print(msg, file=sys.stderr)
        # except IdentifierClientError as nce:
        #     print(
        #         'Command {} failed with HTTP Status code {}, details:\n{}'.
        #         format(subcommand, nce.http_status, nce.message),
        #         file=sys.stderr)
        # except ValueError as ve:
        #     print(ve)

def pretty_print_minid(command_json):
    """Minid specific function to print minid relevant fields to the console
    in a human readable format. Only supports select fields."""
    fields = [
        {
            'title': 'Title',
            'func': lambda m: m['metadata'].get('erc.what')
        },
        {
            'title': 'Checksums',
            'func': lambda m: '\n'.join(['{} ({})'.format(c['value'],
                                                           c['function'])
                                        for c in m['checksums']])
        },
        {
            'title': 'Created',
            'func': lambda m: m['metadata'].get('erc.when')
        },
        {
            'title': 'Landing Page',
            'func': lambda m: m['landing_page']
        },
        {
            'title': 'EZID Landing Page',
            'func': lambda m: ('https://ezid.cdlib.org/id/{}'.format(
                               m['identifier']))
        },
        {
            'title': 'Locations',
            'func': lambda m: ', '.join(m['location'])
        }
    ]
    prepped_lines = [(f['title'], f['func'](command_json)) for f in fields]
    output = ['Minid: {}\n'.format(command_json['identifier'])]
    output.extend(['{0:20} {1}'.format('{}:'.format(title), text or '')
                  for title, text in prepped_lines])
    print('\n'.join(output))