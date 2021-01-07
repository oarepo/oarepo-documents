# -*- coding: utf-8 -*-
"""Defines fixtures available to all tests."""
import os
import shutil
import sys

import pytest
from flask import Flask
from invenio_base.signals import app_loaded
from invenio_db import InvenioDB
from invenio_db import db as _db
from invenio_indexer import InvenioIndexer
from invenio_jsonschemas import InvenioJSONSchemas
from invenio_pidstore import InvenioPIDStore
from invenio_records import InvenioRecords
from invenio_records_rest import InvenioRecordsREST
from invenio_records_rest.utils import PIDConverter
from invenio_records_rest.views import create_blueprint_from_app
from invenio_rest import InvenioREST
from invenio_search import InvenioSearch
from invenio_search.cli import destroy, init
from oarepo_mapping_includes.ext import OARepoMappingIncludesExt
from sample.ext import SampleExt
from sqlalchemy_utils import create_database, database_exists
from oarepo_validate.ext import OARepoValidate

from oarepo_actions.ext import Actions

@pytest.fixture()
def base_app():
    """Flask applicat-ion fixture."""
    instance_path = os.path.join(sys.prefix, 'var', 'tests-instance')

    # empty the instance path
    if os.path.exists(instance_path):
        shutil.rmtree(instance_path)
    os.makedirs(instance_path)

    os.environ['INVENIO_INSTANCE_PATH'] = instance_path

    app_ = Flask('invenio-model-testapp', instance_path=instance_path)
    app_.config.update(
        TESTING=True,
        JSON_AS_ASCII=True,
        SQLALCHEMY_TRACK_MODIFICATIONS=True,
        SQLALCHEMY_DATABASE_URI=os.environ.get(
            'SQLALCHEMY_DATABASE_URI',
            'sqlite:///:memory:'),
        SERVER_NAME='localhost:5000',
        SECURITY_PASSWORD_SALT='TEST_SECURITY_PASSWORD_SALT',
        SECRET_KEY='TEST_SECRET_KEY',
        INVENIO_INSTANCE_PATH=instance_path,
        SEARCH_INDEX_PREFIX='tests-',
        JSONSCHEMAS_HOST='localhost:5000',
        SEARCH_ELASTIC_HOSTS=os.environ.get('SEARCH_ELASTIC_HOSTS', None),
        PIDSTORE_RECID_FIELD='id',
        SUPPORTED_LANGUAGES = ["cs", "en"],
        ELASTICSEARCH_DEFAULT_LANGUAGE_TEMPLATE={
            "type": "text",
            "fields": {
                "keywords": {
                    "type": "keyword"
                }
            }
        }
    )

    InvenioDB(app_)
    InvenioIndexer(app_)
    InvenioSearch(app_)

    return app_


@pytest.yield_fixture()
def app(base_app):
    """Flask application fixture."""

    base_app._internal_jsonschemas = InvenioJSONSchemas(base_app)

    InvenioREST(base_app)
    InvenioRecordsREST(base_app)
    InvenioRecords(base_app)
    #InvenioJSONSchemas(base_app)
    InvenioPIDStore(base_app)
    OARepoValidate(base_app)
    Actions(base_app)
    base_app.url_map.converters['pid'] = PIDConverter
    SampleExt(base_app)
    OARepoMappingIncludesExt(base_app)
    #DocumentRecord(base_app)

    base_app.register_blueprint(create_blueprint_from_app(base_app))

    app_loaded.send(None, app=base_app)

    with base_app.app_context():
        yield base_app


@pytest.yield_fixture()
def client(app):
    """Get tests client."""
    with app.test_client() as client:
        yield client


@pytest.fixture
def db(app):
    """Create database for the tests."""
    with app.app_context():
        if not database_exists(str(_db.engine.url)) and \
                app.config['SQLALCHEMY_DATABASE_URI'] != 'sqlite://':
            create_database(_db.engine.url)
        _db.create_all()

    yield _db

    # Explicitly close DB connection
    _db.session.close()
    _db.drop_all()


@pytest.fixture()
def prepare_es(app, db):
    runner = app.test_cli_runner()
    result = runner.invoke(destroy, ['--yes-i-know', '--force'])
    if result.exit_code:
        print(result.output, file=sys.stderr)
    assert result.exit_code == 0
    result = runner.invoke(init)
    if result.exit_code:
        print(result.output, file=sys.stderr)
    assert result.exit_code == 0
