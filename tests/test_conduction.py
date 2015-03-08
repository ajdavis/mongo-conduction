#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Test Mongo Conduction."""

import logging

import pymongo
from mockupdb import go
from pymongo.errors import OperationFailure

from conduction.server import get_mockup, main_loop
from tests import unittest  # unittest2 on Python 2.6.


class ConductionTest(unittest.TestCase):
    def setUp(self):
        self.mockup = get_mockup(releases={}, env=None,
                                 port=None, verbose=False)
        # Quiet.
        logging.getLogger('mongo_orchestration.apps').setLevel(logging.CRITICAL)
        self.mockup.run()
        self.loop_future = go(main_loop, self.mockup)

        # Cleanups are LIFO: Stop the server, wait for the loop to exit.
        self.addCleanup(self.loop_future)
        self.addCleanup(self.mockup.stop)

        # Any database name will do.
        self.conduction = pymongo.MongoClient(self.mockup.uri).conduction

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


if __name__ == '__main__':
    unittest.main()
