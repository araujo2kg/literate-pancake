import sqlite3
import pytest
from flaskr.db import get_db


def test_get_close_db(app):
    with app.app_context():
        # Checks if get_db returns a connection with the same database always
        db = get_db()
        assert db is get_db()

    # Checks if db.execute raises sqlite ProgrammingError when trying to query outside the app context
    with pytest.raises(sqlite3.ProgrammingError) as e:
        db.execute('SELECT 1')

    assert 'closed' in str(e.value)


# monkeypatch is fixture used to modify/mock parts of the project to test it, in this case we are replacing the init_db function('init-db')
# command, with the fake init_db function, just to check if it is being correctly called    
def test_init_db_command(runner, monkeypatch):
    class Recorder(object):
        called = False

    def fake_init_db():
        Recorder.called = True

    monkeypatch.setattr('flaskr.db.init_db', fake_init_db)
    result = runner.invoke(args=['init-db'])
    assert 'Initialized' in result.output
    assert Recorder.called