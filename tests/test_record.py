import json


def test_createRecord(app, db, client):
    url = "https://localhost:5000/records/document/10.5281/zenodo.3980491"
    response = client.get(url)
    assert response.status_code == 200

    url = "https://localhost:5000/records/document/10.5281/zenodo.3883620"
    response = client.get(url)
    print(response.data)
    assert response.status_code == 200

