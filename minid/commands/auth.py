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
from minid.commands import get_client


@click.command(help='Login with Globus')
@click.option('--remember-me/--no-remember-me', default=False,
              help='Request a refresh token to login indefinitely')
@click.option('--force/--no-force', default=False,
              help='Do a fresh login, ignoring any existing credentials')
@click.option('--local-server/--no-local-server', default=True,
              help='Start a local TCP server to handle the auth code')
@click.option('--browser/--no-browser', default=True,
              help='Automatically open the browser to login')
def login(remember_me, force, local_server, browser):
    mc = get_client()
    if mc.is_logged_in() and not force:
        click.echo('You are already logged in.')
        return

    mc.login(refresh_tokens=remember_me,
             no_local_server=not local_server,
             no_browser=not browser,
             force=force)
    click.secho('You have been logged in.', fg='green')


@click.command(help='Revoke local tokens')
def logout():
    mc = get_client()
    if mc.is_logged_in():
        mc.logout()
        click.secho('You have been logged out.', fg='green')
    else:
        click.echo('No user logged in, no logout necessary.')
