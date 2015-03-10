#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Test Mongo Conduction."""

import logging
import os
from os.path import normpath, expanduser, exists, join

import pymongo
from mockupdb import go
from pymongo.errors import OperationFailure, ConnectionFailure

from conduction.server import get_mockup, main_loop
from tests import unittest  # unittest2 on Python 2.6.

try:
    from collections import OrderedDict
except:
    from ordereddict import OrderedDict  # Python 2.6, "pip install ordereddict"

MONGOBIN = normpath(expanduser(os.environ.get('MONGOBIN', '')))
if not (exists(join(MONGOBIN, 'mongod'))
        or exists(join(MONGOBIN, 'mongod.exe'))):
    raise AssertionError("Couldn't locate mongod, set MONGOBIN environment"
                         " variable to a path containing mongod and mongos")


class ConductionTest(unittest.TestCase):
    def setUp(self):
        releases = OrderedDict([('mongod', MONGOBIN)])
        self.mockup = get_mockup(releases=releases, env=None,
                                 port=None, verbose=False)
        # Quiet.
        logging.getLogger('mongo_orchestration').setLevel(logging.CRITICAL)
        self.mockup.run()
        self.loop_future = go(main_loop, self.mockup)

        # Cleanups are LIFO: Stop the server, wait for the loop to exit.
        self.addCleanup(self.loop_future)
        self.addCleanup(self.mockup.stop)

        # Catch hangs in Conduction or Orchestration.
        client = pymongo.MongoClient(self.mockup.uri, socketTimeoutMS=30000)

        # Any database name will do.
        self.conduction = client.conduction

    def test_root_uri(self):
        reply = self.conduction.command('get', '/')
        self.assertIn('links', reply)
        self.assertIn('service', reply)

    def test_bad_command_name(self):
        with self.assertRaises(OperationFailure) as context:
            self.conduction.command('foo')

        self.assertIn('unrecognized: {"foo": 1}',
                      str(context.exception))

    def test_server_id_404(self):
        with self.assertRaises(OperationFailure) as context:
            self.conduction.command({'post': '/v1/servers/'})

        self.assertIn('404 Not Found', str(context.exception))

    def test_start_basic_server(self):
        try:
            reply = self.conduction.command(
                'post', '/v1/servers',
                body={'preset': 'basic.json', 'id': 'my_id'})
        except OperationFailure as e:
            print(e.details)
            raise

        uri = reply['mongodb_uri']
        client = pymongo.MongoClient(uri, serverSelectionTimeoutMS=500)
        client.admin.command('buildinfo')  # Connects ok.
        self.conduction.command('delete', '/v1/servers/my_id')
        with self.assertRaises(ConnectionFailure):
            client.admin.command('buildinfo')


if __name__ == '__main__':
    unittest.main()
