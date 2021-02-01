# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# invenio-app-ils is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""ILS Document APIs."""

import uuid
from functools import partial

import requests
from crossref.restful import Works
from flask import current_app
from invenio_db import db
from invenio_indexer.api import RecordIndexer
# from invenio_circulation.search.api import search_by_pid
from invenio_pidstore.errors import PersistentIdentifierError
from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from invenio_pidstore.providers.recordid import RecordIdProvider
from invenio_pidstore.providers.recordid_v2 import RecordIdProviderV2
from invenio_records_files.api import Record
# from invenio_app_ils.errors import RecordHasReferencesError
# from invenio_app_ils.fetchers import pid_fetcher
# from invenio_app_ils.minters import pid_minter
# from invenio_app_ils.proxies import current_app_ils
# from invenio_app_ils.records_relations.api import IlsRecordWithRelations
from oarepo_actions.decorators import action
from oarepo_records_draft.record import DraftRecordMixin
from oarepo_validate import MarshmallowValidatedRecordMixin, SchemaKeepingRecordMixin

from .document_json_mapping import schema_mapping
from .marshmallow.document import DocumentSchemaV1
from .minter import document_minter


class DocumentRecordMixin:
    """Class for document record."""

    @classmethod
    @action(detail=False, method="post", url_path="document/<string:first_part>/<string:second_part>")
    def document_by_doi(cls, record_class, first_part=None, second_part=None, **kwargs):
        """Get metadata from DOI."""
        doi = first_part + '/' + second_part
        try:
            pid = PersistentIdentifier.get('recid', doi)
        except:
            pid = None
        if pid != None:
            record = record_class.get_record(pid.object_uuid)
            return record
        else:
            try:
                existing_document = getMetadataFromDOI(doi)
            except:
                pass #todo: what to do here?

        record_uuid = uuid.uuid4()

        data = schema_mapping(existing_document, doi)
        pid, data = document_minter(record_uuid, data)
        record = record_class.create(data=data, id_=record_uuid)
        indexer = RecordIndexer()
        res = indexer.index(record)
        new_doi = PersistentIdentifier.create('recid', doi, object_type='doi',
                                              object_uuid=record_uuid,
                                              status=PIDStatus.RESERVED)

        db.session.commit()
        return record

class CrossRefClient(object):
    """Class for CrossRefClient."""

    def __init__(self, accept='text/x-bibliography; style=apa', timeout=3):
        """
        # Defaults to APA biblio style.

        # Usage:
        s = CrossRefClient()
        print s.doi2apa("10.1038/nature10414")
        """
        self.headers = {'accept': accept}
        self.timeout = timeout

    def query(self, doi, q={}):
        #Get query.
        if doi.startswith("http://"):
            url = doi
        else:
            url = "http://dx.doi.org/" + doi

        r = requests.get(url, headers=self.headers)
        return r

    def doi2apa(self, doi):
        self.headers['accept'] = 'text/x-bibliography; style=apa'
        return self.query(doi).text

    def doi2turtle(self, doi):
        self.headers['accept'] = 'text/turtle'
        return self.query(doi).text

    def doi2json(self, doi):
        self.headers['accept'] = 'application/vnd.citationstyles.csl+json'
        return self.query(doi).json()

    def doi2xml(self, doi):
        self.headers['accept'] = 'application/rdf+xml'
        return self.query(doi).text



def getMetadataFromDOI(id):
    works = Works()
    metadata = works.doi(id)

    if metadata is None:
        s = CrossRefClient()
        metadata = s.doi2json(id)
        #metadata = s.doi2turtle(id)
        #metadata = s.doi2apa(id)
        #metadata = s.doi2xml(id)

    return metadata

