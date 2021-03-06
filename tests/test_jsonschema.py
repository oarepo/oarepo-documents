# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test jsonschema validation."""

import json

from invenio_jsonschemas import current_jsonschemas
from invenio_records.api import Record


def get_schema():
    """This function loads the given schema available"""

    try:
        with open('test_module/jsonschemas/test/test-v1.0.0.json', 'r') as file:
            schema = json.load(file)
    except:
        with open('./tests/test_module/jsonschemas/test/test-v1.0.0.json', 'r') as file:
            schema = json.load(file)

    return schema

def test_json(app):
    """Test of json schema with app."""
    schema = app.extensions['invenio-records']

    data = json.loads('{"these":{"$schema": "xxx", "pid": "xxx", "title" : {"cs": "jej", "en": "yay"}, "authors": [{"full_name":"xxx"}], "publication_year": "1970","document_type":"xx"}}')
    schema.validate(data, get_schema())

    data = json.loads('{"these":{'
                      '"$schema": "xxx", '
                      '"pid": "xxx", '
                      '"title" : {"cs": "jej", "en": "yay"}, '
                      '"authors": [{"full_name":"xxx"}], '
                      '"publication_year": "1970",'
                      '"document_type":"xx", '
                      '"abstract":{"cs": "jej", "en": "yay"}, "alternative_abstracts": {"cs": "jej", "en": "yay"},'
                      '"alternative_titles": {"cs": "jej", "en": "yay"},'
                      '"licenses":[{"license":{"title":{"cs": "jej", "en": "yay"}}}], '
                      '"conference_info": {"title":{"cs": "jej", "en": "yay"}, "place":"xxx"},'
                      '"note":{"cs": "jej", "en": "yay"},'
                      '"publication_info":[{"journal_title":{"cs": "jej", "en": "yay"}}],'
                      '"urls":[{"description": {"cs": "jej", "en": "yay"}, "value":"https://www.cesnet.cz/"}]}}')
    schema.validate(data, get_schema())
    #
    # data = json.loads('{"locations":[{"description": {"cs":"neco", "en-us":"neco jinyho"}, "place": "string"}]}')
    # schema.validate(data, get_schema())
