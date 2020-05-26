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
import datetime
import pytz
import tzlocal

SERVICE_DATE_FORMAT = '%Y-%m-%dT%H:%M:%S.%f'
DATE_FORMAT = '%A, %B %d, %Y %H:%M:%S %Z'


def get_separator():
    return '\n{}'.format('-' * 80)


def get_local_datetime(iso_datestring):
    """Parse an UTC iso datetime string into a python local datetime."""
    if not iso_datestring:
        return ''
    dt = datetime.datetime.strptime(iso_datestring, SERVICE_DATE_FORMAT)
    user_tz = pytz.timezone(tzlocal.get_localzone().zone)
    dt_local = user_tz.fromutc(dt)
    return dt_local.strftime(DATE_FORMAT)


def get_size(size):
    """
    Take an arbitrary number of bytes and parse it into a human readable
    string. Ex: 12GB, 200 bytes, 1ZB
    """
    # Credit to: https://stackoverflow.com/a/1094933
    size = int(size)
    for unit in ['bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB']:
        if abs(size) < 1024:
            if unit == 'bytes':
                return '{} {}'.format(size, unit)
            return '{:.1f}{}'.format(size, unit)
        size /= 1024
    return '{:.1f}{}'.format(size, 'YB')


def pretty_format_minid(cli, command_json):
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
            'func': lambda m: get_size(m.get('metadata', {}).get('length', 0))
        },
        {
            'title': 'Created',
            'func': lambda m: get_local_datetime(m.get('created'))
        },
        {
            'title': 'Updated',
            'func': lambda m: get_local_datetime(m.get('updated'))
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
    return output
