#  -*- coding: utf-8 -*-
# Copyright 2015 MongoDB, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Wire Protocol frontend server to Mongo Orchestration."""

from __future__ import print_function
import argparse

import os
import sys
from io import BytesIO

try:
    # Need simplejson for the object_pairs_hook option in Python 2.6.
    import simplejson as json
except ImportError:
    # Python 2.7+.
    import json

import bottle
import mockupdb
import mongo_orchestration.server
from bson import json_util, SON
from mockupdb import Command

from conduction import __version__

DEFAULT_BIND = os.environ.get('CONDUCTION_HOST', '127.0.0.1')
DEFAULT_PORT = int(os.environ.get('CONDUCTION_PORT', '27017'))

bottle_app = mongo_orchestration.server.get_app()


def parse_args():
    """Return command-line arguments."""
    description = """
Mongo Conduction server.

A wire protocol frontend to Mongo Orchestration, creates and manages MongoDB
configurations on a single host.

THIS PROJECT IS FOR TESTING MONGODB DRIVERS.

http://mongo-conduction.readthedocs.org
"""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-f', '--config',
                        action='store', default=None, type=str, dest='config')
    parser.add_argument('-e', '--env',
                        action='store', type=str, dest='env', default=None)
    parser.add_argument('-b', '--bind',
                        action='store', dest='bind', type=str,
                        default=DEFAULT_BIND)
    parser.add_argument('-p', '--port',
                        action='store', dest='port', type=int,
                        default=DEFAULT_PORT)
    parser.add_argument('-v', '--verbose', dest='verbose',
                        action='store_true', default=False)
    parser.add_argument('--version', action='version',
                        version='Mongo Conduction v' + __version__)

    cli_args = parser.parse_args()

    if cli_args.env and not cli_args.config:
        print("Specified release '%s' without a config file" % cli_args.env)
        sys.exit(1)
    if not cli_args.config:
        return cli_args
    try:
        # Read config.
        with open(cli_args.config, 'r') as fd:
            config = json.loads(fd.read(), object_pairs_hook=SON)
        if 'releases' not in config:
            print("No releases defined in %s" % cli_args.config)
            sys.exit(1)
        releases = config['releases']
        if cli_args.env is not None and cli_args.env not in releases:
            print("Release '%s' is not defined in %s"
                  % (cli_args.env, cli_args.config))
            sys.exit(1)
        cli_args.releases = releases
        return cli_args
    except IOError:
        print("config file not found: %s" % cli_args.config)
        sys.exit(1)


def reply(method, path):
    """Execute request handler and return some JSON."""
    route, args = bottle_app.match({
        'REQUEST_METHOD': method,
        'PATH_INFO': path})

    json_str = route(**args)
    return json.loads(json_str or '{}')


METHODS = set(['get', 'post', 'put', 'delete'])


def main_loop(mockup):
    """Take a running MockupDB server and respond to commands.

    The loop runs forever. Exit with mockup.stop() from another thread.
    """
    assert mockup.port, "Call run() on the MockupDB first"
    for req in mockup:
        if req.matches(Command) and req.command_name.lower() in METHODS:
            try:
                # Request is like: {get: "/servers"}
                # Or: {post: "/servers", body: {preset: "basic.json"}}
                method = req.command_name.lower()
                path = req.doc[req.command_name]
                body = req.doc.get('body', {})

                # Trick Bottle into thinking the wire protocol command's
                # "body" subdocument is a JSON string that is the HTTP
                # POST body.
                body_json_sio = BytesIO(json_util.dumps(body).encode('ascii'))
                environ = {
                    'REQUEST_METHOD': method.upper(),
                    'PATH_INFO': path,
                    'wsgi.input': body_json_sio,
                    'bottle.request.body': body_json_sio
                }
                result = bottle_app._handle(environ)
                if isinstance(result, Exception):
                    raise result
                reply_doc = json.loads(result or '{}')

                if isinstance(reply_doc, list):
                    # Traceback.
                    req.command_err(errmsg='Conduction error',
                                    traceback=reply_doc)
                else:
                    req.ok(reply_doc)
            except bottle.HTTPError as error:
                req.command_err(errmsg=error.status_line)
            except Exception as error:
                req.command_err(errmsg=repr(error))
        else:
            req.command_err(errmsg='unrecognized: %s' % req)


def get_mockup(releases, env, port, verbose):
    mongo_orchestration.server.setup(releases, env)
    mockup = mockupdb.interactive_server(port=port, verbose=verbose,
                                         all_ok=False, name='Conduction')

    # Override the existing buildinfo responder.
    mockup.autoresponds('buildinfo', version='Conduction ' + __version__)
    return mockup


def main():
    args = parse_args()
    mockup = get_mockup(getattr(args, 'releases', {}),
                        args.env,
                        args.port,
                        args.verbose)
    mockup.run()
    print('listening on %s' % mockup.uri)
    try:
        main_loop(mockup)
    except KeyboardInterrupt:
        sys.exit()
    finally:
        print('\nstopping')
        mockup.stop()


if __name__ == '__main__':
    main()
