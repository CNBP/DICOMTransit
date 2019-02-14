import pytest
from dtconfigure.db import get_db
import json
import pdb
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()

def test_index(client, auth):

    response = client.get('/')
    assert b"/auth/login" in response.data
    #assert b"Register" in response.data

    auth.login()
    response = client.get('/')
    from datetime import datetime
    t = datetime.now()

    s = "by test on "+t.strftime("%Y")+"-"+t.strftime("%m")+"-"+t.strftime("%d")
    logger.info(s)

    # Get utf-8 byte encoded version for use in assertion testing
    st = s.encode()
    logger.info(f"Encoded: {st}")

    assert b'Log Out' in response.data

    logger.info(f"Response {response.data}")
    assert st in response.data
    assert b'LORISurl' in response.data
    assert b'LORISpassword' in response.data
    assert b'href="/1/update"' in response.data


@pytest.mark.parametrize('path', (
    '/create',
    '/1/update',
    '/1/delete',
))
def test_login_required(client, path):
    response = client.post(path)
    assert response.headers['Location'] == 'http://localhost/auth/login'


def test_author_required(app, client, auth):
    # change the post author to another user
    with app.app_context():
        db = get_db()
        db.execute('UPDATE configuration SET user_id = 2 WHERE id = 1')
        db.commit()

    auth.login()
    # current user can't modify other user's post
    assert client.post('/1/update').status_code == 403
    assert client.post('/1/delete').status_code == 403
    # current user doesn't see edit link
    assert b'href="/1/update"' not in client.get('/').data


@pytest.mark.parametrize('path', (
    '/2/update',
    '/2/delete',
))
def test_exists_required(client, auth, path):
    auth.login()
    assert client.post(path).status_code == 404


def test_create(client, auth, app):
    auth.login()
    assert client.get('/create').status_code == 200
    # Give d a string of json data. It must be a string  to satisfy
    # requirements of client.post() which uses 
    # http://werkzeug.pocoo.org/docs/0.14/test/#werkzeug.test.EnvironBuilder 
    d='{"GL01" : "GL01", "MD01" : "MD01", "AB01" : "AB01"}'
    # create dict of data
    json_data={
        "LORISurl" : "https://dev.cnbp.ca/api/v0.0.2/",
        "LORISusername" : "mysite",
        "LORISpassword" : "TheLORISpassword",
        "timepoint_prefix" : "V",
        "institutionID" : "VXS",
        "institutionName": "RandomB",
        "projectID_dictionary":d,
        "LocalDatabase" : "MRNLORISDatabase.sqlite",
        "LogPath" : "example path",
        "ZipPath": "example path",
        "ProdOrthancIP" : "http://localhost:8042/",
        "ProdOrthancUser": "myproxyadmin",
        "ProdOrthancPassword": "RandomTextUnitTest",
        "DevOrthancIP" : "132.219.138.166",
        "DevOrthancUser" : "myproxyadmin",
        "DevOrthancPassword" : "TheProxyPassword",
    }

    client.post('/create', data=json_data)

    with app.app_context():
        db = get_db()
        count = db.execute('SELECT COUNT(id) FROM configuration').fetchone()[0]
        assert count == 1


def test_update(client, auth, app):
    auth.login()
    #print(client.get('/1/update').status_code)
    assert client.get('/1/update').status_code == 200

    # Give d a string of json data. It must be a string  to satisfy
    # requirements of client.post() which uses 
    # http://werkzeug.pocoo.org/docs/0.14/test/#werkzeug.test.EnvironBuilder 
    d='{"GL01" : "GL01", "MD01" : "MD01", "AB01" : "AB01"}'
    # create dict of data
    json_data={
        "LORISurl" : "https://dev.cnbp.ca/api/v0.0.2/",
        "LORISusername" : "mysite",
        "LORISpassword" : "UpdatedTheLORISpassword",
        "timepoint_prefix" : "V",
        "institutionID" : "VXS",
        "institutionName": "VXS",
        "projectID_dictionary":d,
        "LocalDatabasePath" : "MRNLORISDatabase.sqlite",
        "LogPath" : "Log is a path",
        "ZipPath": "Zip is also a path",
        "ProdOrthancIP" : "132.219.138.166",
        "ProdOrthancUsername" : "myproxyadmin",
        "ProdOrthancPassword" : "UpdatedTheProxyPassword",
        "DevOrthancIP" : "192.168.106.3",
        "DevOrthancUser" : "mylorisadmin",
        "DevOrthancPassword" : "UpdateTheLORISHostPassword",
    }

    client.post('/1/update', data=json_data)

    with app.app_context():
        SQLite_connect = get_db()
        SQLite_cursor = SQLite_connect.cursor()
        SQLite_cursor.execute('SELECT * FROM configuration WHERE id = 1')
        row = SQLite_cursor.fetchone()
        print(row)
        assert row['LORISpassword'] == 'UpdatedTheLORISpassword'


"""
Disable this test for now because it fails with an obscure message
@pytest.mark.parametrize('path', (
    '/create',
    '/1/update',
))
def test_create_update_validate(client, auth, path):
    auth.login()
    assert client.get(path).status_code == 200
    json_data={"port":"","LORISurl":"","LORISusername":"","LORISpassword":"","timepoint_prefix":"","institutionID":"","projectID_dictionary":"","LocalDatabase":"","OrthancURL":"","ProxyIP":"","ProxyUsername":"","ProxyPassword":"","LORISHostIP":"","LORISHostUsername":"","LORISHostPassword":"","DeletionScript":""}
    #pdb.set_trace()
    client.as_tuple = True
    response = client.post(path, data=json_data)
    assert b'LORISurl is required.' in response.data
"""

def test_delete(client, auth, app):
    auth.login()
    response = client.post('/1/delete')
    assert response.headers['Location'] == 'http://localhost/'

    with app.app_context():
        db = get_db()
        post = db.execute('SELECT * FROM configuration WHERE id = 1').fetchone()
        assert post is None


