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

# try:
#     # try to use files enabled record
#     from invenio_records_files.api import Record
# except ImportError:
#     # and fall back to normal record
#     from invenio_records.api import Record


class DocumentRecordMixin:

    @classmethod
    @action(detail=False, url_path="document/<string:first_part>/<string:second_part>")
    def document_by_doi(cls, record_class, first_part=None, second_part=None, **kwargs):
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
                #todo jaka ma byt zabavna hlaska?
                return {"doi" :"does not eixst"} #az na to ze tohle rozhodne jinak...

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

    def __init__(self, accept='text/x-bibliography; style=apa', timeout=3):
        """
        # Defaults to APA biblio style

        # Usage:
        s = CrossRefClient()
        print s.doi2apa("10.1038/nature10414")
        """
        self.headers = {'accept': accept}
        self.timeout = timeout

    def query(self, doi, q={}):
        if doi.startswith("http://"):
            url = doi
        else:
            url = "http://dx.doi.org/" + doi

        r = requests.get(url, headers=self.headers)
        print(r)
        return r

    def doi2apa(self, doi):
        self.headers['accept'] = 'text/x-bibliography; style=apa'
        return self.query(doi).text

    def doi2turtle(self, doi):
        self.headers['accept'] = 'text/turtle'
        return self.query(doi).text

    def doi2json(self, doi):
        self.headers['accept'] = 'application/vnd.citationstyles.csl+json'
        print(self.query(doi).text)
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

# class SampleDraftRecord(DraftRecordMixin, DocumentRecord):
#     pass


# DOCUMENT_PID_TYPE = "docid"
# DOCUMENT_PID_MINTER = "docid"
# DOCUMENT_PID_FETCHER = "docid"
#
# DocumentIdProvider = type(
#     "DocumentIdProvider",
#     (RecordIdProviderV2,),
#     dict(pid_type=DOCUMENT_PID_TYPE, default_status=PIDStatus.REGISTERED),
# )
# document_pid_minter = partial(pid_minter, provider_cls=DocumentIdProvider)
# document_pid_fetcher = partial(pid_fetcher, provider_cls=DocumentIdProvider)
#
#
# class Document(IlsRecordWithRelations):
#     """Document record class."""
#
#     DOCUMENT_TYPES = [
#         "BOOK",
#         "PROCEEDING",
#         "STANDARD",
#         "PERIODICAL_ISSUE",
#     ]
#
#     _pid_type = DOCUMENT_PID_TYPE
#     _schema = "documents/document-v1.0.0.json"
#     _circulation_resolver_path = (
#         "{scheme}://{host}/api/resolver/documents/{document_pid}/circulation"
#     )
#     _item_resolver_path = (
#         "{scheme}://{host}/api/resolver/documents/{document_pid}/items"
#     )
#     _eitem_resolver_path = (
#         "{scheme}://{host}/api/resolver/documents/{document_pid}/eitems"
#     )
#     _relations_path = (
#         "{scheme}://{host}/api/resolver/documents/{document_pid}/relations"
#     )
#     _stock_resolver_path = (
#         "{scheme}://{host}/api/resolver/documents/{document_pid}/stock"
#     )
#
#     @classmethod
#     def build_resolver_fields(cls, data):
#         """Build all resolver fields."""
#         data["circulation"] = {
#             "$ref": cls._circulation_resolver_path.format(
#                 scheme=current_app.config["JSONSCHEMAS_URL_SCHEME"],
#                 host=current_app.config["JSONSCHEMAS_HOST"],
#                 document_pid=data["pid"],
#             )
#         }
#         data.setdefault("relations", {})
#         data["relations"] = {
#             "$ref": cls._relations_path.format(
#                 scheme=current_app.config["JSONSCHEMAS_URL_SCHEME"],
#                 host=current_app.config["JSONSCHEMAS_HOST"],
#                 document_pid=data["pid"],
#             )
#         }
#         data.setdefault("eitems", {})
#         data["eitems"] = {
#             "$ref": cls._eitem_resolver_path.format(
#                 scheme=current_app.config["JSONSCHEMAS_URL_SCHEME"],
#                 host=current_app.config["JSONSCHEMAS_HOST"],
#                 document_pid=data["pid"],
#             )
#         }
#         data.setdefault("items", {})
#         data["items"] = {
#             "$ref": cls._item_resolver_path.format(
#                 scheme=current_app.config["JSONSCHEMAS_URL_SCHEME"],
#                 host=current_app.config["JSONSCHEMAS_HOST"],
#                 document_pid=data["pid"],
#             )
#         }
#         data["stock"] = {
#             "$ref": cls._stock_resolver_path.format(
#                 scheme=current_app.config["JSONSCHEMAS_URL_SCHEME"],
#                 host=current_app.config["JSONSCHEMAS_HOST"],
#                 document_pid=data["pid"],
#             )
#         }
#
#     @classmethod
#     def create(cls, data, id_=None, **kwargs):
#         """Create Document record."""
#         cls.build_resolver_fields(data)
#         return super().create(data, id_=id_, **kwargs)
#
#     def update(self, *args, **kwargs):
#         """Update Document record."""
#         super().update(*args, **kwargs)
#         self.build_resolver_fields(self)
#
#     def delete(self, **kwargs):
#         """Delete Document record."""
#         loan_search_res = search_by_pid(
#             document_pid=self["pid"],
#             filter_states=["PENDING"]
#             + current_app.config["CIRCULATION_STATES_LOAN_ACTIVE"],
#         )
#         if loan_search_res.count():
#             raise RecordHasReferencesError(
#                 record_type="Document",
#                 record_id=self["pid"],
#                 ref_type="Loan",
#                 ref_ids=sorted([res["pid"] for res in loan_search_res.scan()]),
#             )
#
#         item_search = current_app_ils.item_search_cls()
#         item_search_res = item_search.search_by_document_pid(
#             document_pid=self["pid"]
#         )
#         if item_search_res.count():
#             raise RecordHasReferencesError(
#                 record_type="Document",
#                 record_id=self["pid"],
#                 ref_type="Item",
#                 ref_ids=sorted([res["pid"] for res in item_search_res.scan()]),
#             )
#
#         req_search = current_app_ils.document_request_search_cls()
#         req_search_res = req_search.search_by_document_pid(
#             document_pid=self["pid"]
#         )
#         if req_search_res.count():
#             raise RecordHasReferencesError(
#                 record_type="Document",
#                 record_id=self["pid"],
#                 ref_type="DocumentRequest",
#                 ref_ids=sorted([res["pid"] for res in req_search_res.scan()]),
#             )
#
#         return super().delete(**kwargs)
#
#
# def document_exists(document_pid):
#     """Return True if the Document exists given a PID."""
#     Document = current_app_ils.document_record_cls
#     try:
#         Document.get_record_by_pid(document_pid)
#     except PersistentIdentifierError:
#         return False
#     return True
