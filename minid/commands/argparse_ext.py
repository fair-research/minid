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

# Pattern inspired and built from:
# https://gist.github.com/mivade/384c2c41c3a29c637cb6c603d4197f9f


def argument(*name_or_flags, **kwargs):
    """Convenience function to properly format arguments to pass to the
    subcommand decorator.
    """
    return list(name_or_flags), kwargs


def shared_argument(arg):
    """Convenience function that denotes this argument is used in multiple
    places."""
    return arg


def parse_none_values(values, none_value='None'):
    """
    Allows users to specify null values to unset options. For example, if
    someone mistakenly added 'replaced' on a minid and wanted to remove it,
    they could pass `minid update minid:123 --replaces None`
    ** Parameters **
    values -- A list of three tuple items. For example
    [
        ('replaces', args.replaces, None),
        ('replaced_by', args.replaced_by, None),
        ('locations', args.locations, []),
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


def subcommand(args, parent, **kwargs):
    def decorator(func):
        shared_args = kwargs.pop('shared_arguments', {})
        parser = parent.add_parser(
            func.__name__.replace('_', '-'),
            description=func.__doc__,
            **kwargs)
        for arg in args:
            if isinstance(arg, tuple):
                arg_name, kw_args = arg
                parser.add_argument(*arg_name, **kw_args)
            elif isinstance(arg, str):
                arg_name = [arg]
                kw_args = shared_args.get(arg)
                if not arg:
                    raise ValueError('Shared argument {} not found in {}'
                                     ''.format(arg_name, func.__name__))
                parser.add_argument(*arg_name, **kw_args)
            else:
                raise ValueError('Invalid subcommand {} for {}'.format(
                    arg, func.__name__))

        parser.set_defaults(func=func)
        return func

    return decorator
