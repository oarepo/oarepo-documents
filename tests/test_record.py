
def test_createRecord(app, db, client):
    url = "https://localhost:5000/records/document/10.5281/zenodo.3980491"
    response = client.post(url)
    assert response.status_code == 302

    url = response.headers["Location"]
    assert url == 'https://localhost:5000/records/1'
    response = client.get(url)
    assert response.status_code == 200

    url = "https://localhost:5000/records/document/10.5281/zenodo.3883620"
    response = client.post(url)
    assert response.status_code == 302


    url = "https://localhost:5000/records/document/10.5281/zenodo.3784952"
    response = client.post(url)
    assert response.status_code == 302

    url = "https://localhost:5000/records/document/10.5281/zenodo.4108300"
    response = client.post(url)
    assert response.status_code == 302

    url = "https://localhost:5000/records/document/10.5281/zenodo.4108306"
    response = client.post(url)
    assert response.status_code == 302

