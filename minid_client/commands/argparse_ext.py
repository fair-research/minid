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


def subcommand(args, parent, **kwargs):
    def decorator(func):
        parser = parent.add_parser(
            func.__name__.replace('_', '-'),
            description=func.__doc__,
            **kwargs)
        for arg in args:
            parser.add_argument(*arg[0], **arg[1])
        parser.set_defaults(func=func)
        return func

    return decorator
