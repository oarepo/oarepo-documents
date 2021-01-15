from oarepo_documents.document_json_mapping import schema_mapping



def test_createRecord(app, db, client):
    existing_document =  {"categories": ["X", "yy", "kchchch", "K", "J", "x", "xxx", "xxxxxx"], "titles": ["Nějaká úžasná česká věta"]}
    data = schema_mapping(existing_document, 'doi')
    assert data == {'alternative_identifiers': [{'scheme': 'DOI', 'value': 'doi'}],
                    'authors': [{'full_name': 'Various authors'}],
                    'categories': [{'value': 'X yy kchchch'},
                                    {'value': 'K'},
                                    {'value': 'J x xxx xxxxxx'}],
                    'document_type': 'unknown',
                    'publication_year': 'unknown',
                    'title': {"cs": "Nějaká úžasná česká věta"}}

    existing_document = {"titles": "Willst du bis der Tod euch scheidet treu ihr sein für alle Tage? Nein!",
                         "authors": [{"given": "givenname", "family": "familyname"}, {"given": "givenname1", "family": "familyname2"}]}
    data = schema_mapping(existing_document, 'doi')
    assert data == {'alternative_identifiers': [{'scheme': 'DOI', 'value': 'doi'}],
                    'authors': [{'full_name': 'givenname familyname'},
                                {'full_name': 'givenname1 familyname2'}],
                    'document_type': 'unknown',
                    'publication_year': 'unknown',
                    'title': {"de": "Willst du bis der Tod euch scheidet treu ihr sein für alle Tage? Nein!"}
                    }