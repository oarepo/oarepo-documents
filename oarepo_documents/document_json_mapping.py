from deepmerge import always_merger
from langdetect import detect_langs, detect

def try_name(nlist,record, default=None):
    for name in nlist:
        try:
            return record[name]
        except:
            continue
    else:
        return default

def schema_mapping(existing_record, doi):
    data = {}

    #abstract - multilingual --- mezivalidacky!
    abstract_value =  try_name(nlist = ['abstract', 'abstracts'], record =existing_record)
    if abstract_value != None:
        probability = detect_langs(abstract_value)
        if probability[0].prob >= 0.99999:
            abstract_language = probability[0].lang
        else:
            abstract_language = '??'  # unknown language

        abstract = {abstract_language: abstract_value}
        always_merger.merge(data, {'abstract': abstract})

    #alternative_abstracts - array of strings
    alternative_abstract = try_name(['alternative_abstract', 'alternative_abstracts'], existing_record)
    if alternative_abstract != None:
        if(type(alternative_abstract) is list):
            is_string = True
            for a in alternative_abstract:
                if type(a) is not str:
                    is_string = False
                    break
            if is_string:
                aa = {}
                for a in alternative_abstract:
                    probability = detect_langs(a)
                    if probability[0].prob >= 0.99999:
                        abstract_language = probability[0].lang
                    else:
                        abstract_language = '??'  # unknown language

                    abstract = {abstract_language: a}
                    aa = always_merger.merge(aa, abstract)

                always_merger.merge(data, {'alternative_abstracts': aa})

    #alternative_identifiers
    always_merger.merge(data, {"alternative_identifiers": [{"scheme": "DOI", "value": doi}]})

    #alternative_titles
    alternative_titles = try_name(['alternative_title', 'alternative_titles', 'shor-contrainer-title'], existing_record)
    if alternative_titles != None:
        if (type(alternative_titles) is list):
            is_string = True
            for a in alternative_titles:
                if type(a) is not str:
                    is_string = False
                    break
            if is_string:
                aa = {}
                for a in alternative_titles:
                    probability = detect_langs(a)
                    if probability[0].prob >= 0.99999:
                        title_language = probability[0].lang
                    else:
                        title_language = '??'  # unknown language

                    title = {title_language: a}
                    aa = always_merger.merge(aa, title)
                always_merger.merge(data, {'alternative_titles': aa})

    #authors
    authors_array = try_name(nlist=['authors', 'author', 'contributor', 'contributors'], record=existing_record)
    if authors_array == None:
        always_merger.merge(data, {'authors': [{"full_name": "Various authors"}]}) #default
    else:
        if(type(authors_array) is list):
            authors_data = []
            for author in authors_array:
                a_data = {}
                if 'ORCID' in author:
                    always_merger.merge(a_data, {"identifiers": [{"schema": "ORCID", "value": author["ORCID"]}]})
                if 'alternative_names' in author and type(author['alternative_names']) is list:
                    always_merger.merge(a_data, {"alternative_names": author['alternative_names']})
                if 'roles' in author and type(author['roles']) is list:
                    always_merger.merge(a_data, {"roles": author['roles']})
                if 'type' in author and type(author['type']) is str:
                    always_merger.merge(a_data, {"type": author['type']})
                #affiliation /affiliations
                full_name = try_name(nlist=['full_name', 'name', 'fullname'], record=author)
                if full_name != None:
                    always_merger.merge(a_data, {"full_name": full_name})
                    authors_data.append(a_data)
                    continue
                given = try_name(nlist=['given', 'first', 'first_name'], record=author)
                family = try_name(nlist=['family', 'family_name', 'second_name'], record=author)
                if(given == None or family == None):
                    always_merger.merge(a_data, {"full_name": "unknown"})
                    authors_data.append(a_data)
                    continue
                else:
                    full_name = given + " " + family
                    always_merger.merge(a_data, {"full_name": full_name})
                    authors_data.append(a_data)
                    continue


            always_merger.merge(data, {'authors': authors_data})

    # document_type
    doctype = try_name(nlist=['document_type', 'type'], record=existing_record)
    if doctype == None:
        always_merger.merge(data, {'document_type': "unknown"})  # default
    else:
        always_merger.merge(data, {'document_type': doctype})

    #publication_year
    publication_year = try_name(nlist=['publication_year', 'issued'], record=existing_record)

    if publication_year != None and type(publication_year) is str and len(publication_year['data-part'][0]) == 4:
        always_merger.merge(data, {'publication_year': publication_year})
    elif publication_year != None and type(publication_year) is dict:
        if 'date-parts' in publication_year.keys():
            if len(str(publication_year['date-parts'][0][0])) == 4:
                always_merger.merge(data, {'publication_year': str(publication_year['date-parts'][0][0])})
            else:
                always_merger.merge(data, {'publication_year': "unknown"})
        else:
            always_merger.merge(data, {'publication_year': "unknown"})
    else:
        always_merger.merge(data, {'publication_year': "unknown"})

    # title - multilingual --- mezivalidacky!
    title_value = try_name(nlist=['title', 'titles'], record=existing_record)
    if title_value != None:
        if type(title_value) is list:
            title_value= title_value[0]
        probability = detect_langs(title_value)
        if probability[0].prob >= 0.99999:
            title_language = probability[0].lang
        else:
            title_language = '??'  # unknown language

        title = {title_language: title_value}
        always_merger.merge(data, {'title': title})
    else:
        always_merger.merge(data, {'title': "unknown"}) #default

    return data