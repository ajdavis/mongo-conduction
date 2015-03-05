.. mongo-conduction documentation master file, created by
   sphinx-quickstart on Tue Jul  9 22:26:36 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Mongo Conduction
================

.. image:: _static/conduction.jpg

Wire Protocol frontend server to `Mongo Orchestration`_.

Follow :doc:`installation` instructions, then::

    $ mongo-conduction
    listening on mongodb://localhost:27017

Connect with the mongo shell::

    $ mongo
    Server has startup warnings:
    hello from Conduction!
    Conduction:PRIMARY>

Conduction translates Mongo Orchestration's REST API to MongoDB Wire Protocol
commands straightforwardly::

    Conduction:PRIMARY> var info = db.runCommand({
    ...    post:'/servers',
    ...    body: {name: "mongod", preset: "basic.json"}
    ... })
    Conduction:PRIMARY> info
    {
        "links" : [
            {
                "href" : "/v1/servers/f38a4d1c-815e-4daf-9744-960a25bf16f4",
                "method" : "DELETE",
                "rel" : "delete-server"
            },
            {
                "href" : "/v1/servers/f38a4d1c-815e-4daf-9744-960a25bf16f4",
                "method" : "GET",
                "rel" : "get-server-info"
            }
        ],
        // ... lots more info ...
    	"mongodb_uri" : "mongodb://127.0.0.1:1027",
    }

Find the link for server info::

    Conduction:PRIMARY> info_link = info.links.filter(function(link) {
    ...    return link.rel == "get-server-info";
    ... })[0]
    {
        "href" : "/v1/servers/f38a4d1c-815e-4daf-9744-960a25bf16f4",
        "method" : "GET",
        "rel" : "get-server-info"
    }
    Conduction:PRIMARY> db.runCommand({get: info_link.href})
    {
        "procInfo" : {
            // ... lots of info ...
        }
    }

Shut a server down::

    Conduction:PRIMARY> delete_link = info.links.filter(function(link) { return link.rel == "delete-server"; })[0]
    {
        "href" : "/v1/servers/f38a4d1c-815e-4daf-9744-960a25bf16f4",
        "method" : "DELETE",
        "rel" : "delete-server"
    }
    Conduction:PRIMARY> db.runCommand({delete: delete_link.href})
    { "ok" : 1 }

Contents:

.. toctree::
   :maxdepth: 1

   readme
   installation
   usage
   contributing
   authors
   changelog

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Image Credit: `Ed Ouimette <https://www.flickr.com/photos/ejoui15/9333213382/>`_

.. _Mongo Orchestration: https://github.com/10gen/mongo-orchestration
