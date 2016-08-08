#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division

import pytest
import mongomock

import doorman
from doorman.webserver import app as doorman_app


db = mongomock.MongoClient().db.resources
db.ensure_index('id', unique=True)


@pytest.fixture(scope="session")
def app():
    def get_resources_db_mock():
        return db
    doorman.webserver.get_resources_db = get_resources_db_mock
    doorman_app.config["DEBUG"] = True
    doorman_app.config["TESTING"] = True
    return doorman_app
