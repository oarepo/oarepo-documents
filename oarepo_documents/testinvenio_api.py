# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 alzp.
#
# testInvenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Records API."""

from __future__ import absolute_import, print_function

import json
import uuid

import invenio_records
from invenio_pidstore.providers.recordid import RecordIdProvider
from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from invenio_pidstore.resolver import Resolver
from invenio_records_files.api import Record as FilesRecord
from oarepo_actions.decorators import action
from invenio_pidstore import resolver
from crossref.restful import Works
import requests
import subprocess
from invenio_db import db
#from invenio_records import Record

from invenio_records_rest.schemas.fields import PersistentIdentifier as PersistentID
from invenio_records import Record as Rec
class Record(FilesRecord):
    """Custom record."""

    # @classmethod
    # @action(detail=False, url_path="c/<string:param1>/<string:param2>")
    # def blah111(cls, param1=None, param2=None, **kwargs):
    #     doi = param1 + '/' + param2
    #     try:
    #         pid = PersistentIdentifier.get('recid', doi)
    #     except:
    #         pid = None
    #     if pid != None:
    #         record = Record.get_record(pid.object_uuid, with_deleted=True)
    #     else:
    #         return {"n": "ic"}

    @classmethod
    @action(detail=False, url_path="document/<string:first_part>/<string:second_part>")
    def document(cls,first_part=None, second_part=None, **kwargs):
        doi = first_part + '/' + second_part
        try:
            pid = PersistentIdentifier.get('recid', doi)
            print(pid)
        except:
            pid = None
        if pid != None:
            record = Record.get_record(pid.object_uuid, with_deleted=True)
            return record
        else:

            try:
                existing_document = getMetafataFromDOI(doi)
            except:
                return {"doi": "does not exist"}

            req = requests.post('https://localhost:5000/api/records/', json={"title": existing_document['title'], "contributors":[{"name": "neco"}]}, verify=False)


            db.session.commit()
            json_str = json.dumps(req.json())
            json_object = json.loads(json_str)
            new_record_id = json_object['id']
            new_record_pid = PersistentIdentifier.get('recid', new_record_id)

            new_doi = PersistentIdentifier.create('recid', doi, object_type='doi',
                                                                                object_uuid=new_record_pid.object_uuid,
                                                                                status=PIDStatus.RESERVED)

            db.session.commit()


            return json_object



    _schema = "records/record-v1.0.0.json"

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
        return self.query(doi).json()


def getMetafataFromDOI(id):
    works = Works()
    metadata = works.doi(id)

    if metadata is None:
        s = CrossRefClient()
        metadata = s.doi2json(id)

    return metadata
