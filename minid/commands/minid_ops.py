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
import click
from minid.commands import get_client, formatting
from minid.version import __VERSION__

log = logging.getLogger(__name__)


def parse_none_values(values, none_value='None'):
    """
    Allows users to specify null values to unset options. For example, if
    someone mistakenly added 'replaced' on a minid and wanted to remove it,
    they could pass `minid update minid:123 --replaces None`
    ** Parameters **
    values -- A list of three tuple items. For example
    [
        ('replaces', replaces, None),
        ('replaced_by', replaced_by, None),
        ('locations', locations, []),
    ]
    Where each item is (name, value, This option's "None" value)

    none_value -- The user-input value that indicates the option should be
    set to None
    """
    options = {}
    for option_name, option_value, option_none_value in values:
        if isinstance(option_value, str) and option_value == none_value:
            options[option_name] = option_none_value
        elif isinstance(option_value, list) and option_value == [none_value]:
            options[option_name] = option_none_value
        elif option_value:
            options[option_name] = option_value
    return options


def print_minids(identifier_response, output_json=False):
    minids = identifier_response.get('identifiers', [identifier_response])
    if output_json is True:
        output = json.dumps(minids, indent=2)
    else:
        mc = get_client()
        output = [formatting.pretty_format_minid(mc, minid) for minid in minids]
        output = formatting.get_separator().join(output)
    click.echo(output)


def json_option(func):
    return click.option('--json/--no-json', '-j', is_flag=True, default=False, help='Output as JSON')(func)


def test_option(func):
    return click.option('--test/--no-test', default=False, help='Create a temporary test Minid')(func)


@click.command()
@click.argument('filename', type=click.Path())
@click.option('--title', default=False, help='Add a title for the Minid.')
@click.option('--locations', help='Remote locations where files can be retrieved')
@click.option('--replaces', help='Replace another Minid with this Minid')
@test_option
@json_option
def register(filename, title, locations, replaces, test, json):
    """Register a Minid for a file. """
    mc = get_client()
    kwargs = dict()
    # ONLY add replaces if we intend to actually replace the Minid
    if replaces:
        kwargs['replaces'] = replaces
    minid = mc.register_file(filename, title=title, locations=locations.split(','), test=test, **kwargs)
    print_minids(minid.data, output_json=json)


@click.command(help='Register a batch of Minids from an RFM or file stream')
@click.argument('filename', type=click.Path())
@test_option
def batch_register(filename, test):
    """Register a batch of Minids from an RFM or file stream

    Batch Register can either be passed a file to a Remote File Manifest JSON
    file, or streamed where each entry in the stream is an RFM formatted dict.
    """
    click.echo(json.dumps(get_client().batch_register(filename, test), indent=2))


@click.command(help='Update an existing Minid')
@click.argument('minid', type=click.Path())
@click.option('--title', default=False, help='Add a title for the Minid.')
@click.option('--locations', help='Remote locations where files can be retrieved')
@click.option('--replaces', help='Replace another Minid with this Minid')
@click.option('--replaced-by', help='Minid replacing this one. "None" to clear.')
@click.option('--set-active', help='Set Minid active')
@click.option('--set-inactive', help='Set Minid inactive')
@json_option
def update(minid, title, locations, replaces, replaced_by, set_active, set_inactive, json):
    kwargs = dict()
    if set_active and set_inactive:
        click.secho('Cannot use both --set-active and --set-inactive', bg='red')
        return
    if set_active or set_inactive:
        kwargs['active'] = True if set_active else False

    optional_values = [
        ('replaces', replaces, None),
        ('replaced_by', replaced_by, None),
        ('locations', locations.split(','), []),
    ]

    kwargs.update(parse_none_values(optional_values))
    minid = get_client().update(minid, title=title, **kwargs)
    print_minids(minid.data, output_json=json)


@click.command()
@click.argument('entity')
@click.option('--function', default='sha256', help='function used to generate the checksum, if provided')
@json_option
def check(entity, function, json):
    """Lookup a minid or check if a given file has been registered"""
    print_minids(get_client().check(entity, function).data, output_json=json)


@click.command()
def version():
    """Print version and exit"""
    click.echo(__VERSION__)
