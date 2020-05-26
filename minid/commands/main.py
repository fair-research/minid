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
import click
import sys
import os
import logging

if __name__ == '__main__':
    # Setup pathing
    module = os.path.abspath(__file__)
    path = os.path.dirname(os.path.dirname(os.path.dirname(module)))
    sys.path.insert(0, path)

from minid.commands import auth, minid_ops
from minid import exc

log = logging.getLogger(__name__)


class MainCommandGroup(click.Group):
    """Override invoke to catch top level errors"""
    def invoke(self, ctx):
        try:
            return super(MainCommandGroup, self).invoke(ctx)
        except exc.LoginRequired:
            click.secho('You need to login first', err=True)
            click.get_current_context().exit(1)
        except Exception as e:
            log.exception(e)
            click.secho(f'{str(e)}', err=True)
            click.get_current_context().exit(1)


def main_group(*args, **kwargs):
    def inner_func(f):
        return click.group(*args, cls=MainCommandGroup, **kwargs)(f)
    return inner_func


@main_group()
def cli():
    pass


cli.add_command(auth.login)
cli.add_command(auth.logout)
cli.add_command(minid_ops.register)
cli.add_command(minid_ops.batch_register)
cli.add_command(minid_ops.update)
cli.add_command(minid_ops.check)
cli.add_command(minid_ops.version)


if __name__ == '__main__':
    cli()
