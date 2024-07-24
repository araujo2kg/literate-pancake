"""
conftest is a pytest configuration file,
every fixture here will be accessible in all of
the files in the tests directory.
it too should be used to define setup and teardown methods
"""
import os
import tempfile
import pytest
from flaskr import create_app
from flaskr.db import get_db, init_db

with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
    _data_sql = f.read().decode('utf8')

    
# pytest fixture basically creates a setup for the tests to run
@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()

    # as configured in the froundy, when the config is passed to create_app, it runs it, in this is instanciating the app in test mode
    app = create_app({
        'TESTING': True,
        'DATABASE': db_path,
    })
    
    with app.app_context():
        init_db()
        get_db().executescript(_data_sql)

    yield app

    # Used to cleanup the temp file after the test is done
    os.close(db_fd)
    os.unlink(db_path)


# test_client() is a default method of the flask app testing utilities, used to simulate http requests without a server
# returns the client object that can be used to make the tests
# this fixture automatically calls the app fixture to receive an instance of the app
@pytest.fixture
def client(app):
    return app.test_client()

    
# test_cli_runner() is a default method of the flask app testing utilities, used to call click commands registered in the app instance
# returns the runner object that can be used to make the tests
# this fixture automatically calls the app fixture to receive an instance of the app
@pytest.fixture
def runner(app):
    return app.test_cli_runner()


# Utilizes the client object make a login and logout attempt
class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, username='test', password='test'):
        return self._client.post(
            '/auth/login',
            data={'username': username, 'password': password}
        )

    def logout(self):
        return self._client.get('/auth/logout')


# this fixture automatically calls the client fixture to get an instance of test_client
@pytest.fixture
def auth(client):
    return AuthActions(client)