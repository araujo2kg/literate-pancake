import pytest
from flaskr.db import get_db


# If the user os logged in or not the content displayed on index is different
def test_index(client, auth):
    response = client.get("/")
    assert b"Log In" in response.data
    assert b"Register" in response.data
    assert b"Like | 1" in response.data
    assert b"Dislike | 0" in response.data
    assert b"/comments/create" in response.data
    assert b"#tagname" in response.data
    assert b'href="/tag/tagname/"' in response.data

    auth.login()
    response = client.get("/")
    assert b"Log Out" in response.data
    assert b"test title" in response.data
    assert b"by test on 2018-01-01" in response.data
    assert b"test\nbody" in response.data
    assert b'href="/1/update"' in response.data
    assert b"Like | 1" in response.data
    assert b"Dislike | 0" in response.data


@pytest.mark.parametrize(
    "path",
    (
        "/create",
        "/1/update",
        "/1/delete",
    ),
)
def test_login_required(client, path):
    response = client.post(path)
    assert response.headers["Location"] == "/auth/login"


def test_author_required(app, client, auth):
    # change the post author to another user (test default is 1)
    with app.app_context():
        db = get_db()
        db.execute("UPDATE post SET author_id = 2 WHERE id = 1")
        db.commit()

    auth.login()
    # current user cannot modify other user's post
    assert client.post("/1/update").status_code == 403
    assert client.post("/1/delete").status_code == 403
    # current user does not see edit link
    assert b'href="/1/update"' not in client.get("/").data


@pytest.mark.parametrize(
    "path",
    (
        "/2/update",
        "/2/delete",
    ),
)
def test_exists_required(client, auth, path):
    auth.login()
    assert client.post(path).status_code == 404


def test_create(client, auth, app):
    auth.login()
    assert client.get("/create").status_code == 200
    # Insert a new element in the post table
    client.post("/create", data={"title": "created", "body": "hello there", "tags": '[{"value": "tag1"}, {"value": "tag2"}]'})

    with app.app_context():
        db = get_db()
        # Check if the new row was added (test post table contains 1 registry)
        count = db.execute("SELECT COUNT(id) FROM post").fetchone()[0]
        assert count == 2

    # New post with no tags
    assert client.post("/create", data={"title": "created", "body": "hello there", "tags": ""}).status_code == 302


def test_update(client, auth, app):
    auth.login()
    assert client.get("/1/update").status_code == 200
    # Update the element in the post table (1)
    client.post("/1/update", data={"title": "updated", "body": "", "tags": ""})

    with app.app_context():
        db = get_db()
        # Check if it was updated
        post = db.execute("SELECT * FROM post WHERE id = 1").fetchone()
        assert post["title"] == "updated"

    # Update element with tags
    assert client.post("/1/update", data={"title": "updated", "body": "", "tags": '[{"value": "tag1"}, {"value": "tag2"}]'}).status_code == 302


@pytest.mark.parametrize(
    "path",
    (
        "/create",
        "/1/update",
    ),
)
def test_create_update_validate(client, auth, path):
    auth.login()
    response = client.post(path, data={"title": "", "body": "", "tags": ""})
    assert b"Title is required." in response.data


def test_delete(client, auth, app):
    auth.login()
    # Post to delete view, that should remove the /1/ post&reactions&comments and redirect to index
    response = client.post("/1/delete")
    assert response.headers["Location"] == "/"

    # Checks if post, reactions and comments were deleted
    with app.app_context():
        db = get_db()
        reactions = db.execute("SELECT * FROM reactions WHERE post_id = 1").fetchone()
        comments = db.execute("SELECT * FROM comments WHERE post_id = 1").fetchone()
        post = db.execute("SELECT * FROM post WHERE id = 1").fetchone()
        assert post is None
        assert reactions is None
        assert comments is None


def test_post(client, auth):
    response = client.get("/1/post")
    assert response.status_code == 200
    assert b"test title" in response.data
    assert b'href="/1/update"' not in response.data
    assert b"Like | 1" in response.data
    assert b"Dislike | 0" in response.data
    assert b"/comments/create" in response.data
    assert b"#tagname" in response.data
    assert b'href="/tag/tagname/"' in response.data

    auth.login()
    response = client.get("/1/post")
    assert b'href="/1/update"' in response.data
    assert b"Like | 1" in response.data
    assert b"Dislike | 0" in response.data
    assert b'href="/comments/1/update"' in response.data
    assert b"comment body test" in response.data


def test_reactions(client, auth, app):
    # like in post with id 1 not logged, should redirect to login page
    response = client.post("/0/1/reaction")
    assert response.headers["Location"] == "/auth/login"

    auth.login()
    # Dislike in post with id 1
    response = client.post("/1/1/reaction")
    assert b"updated" in response.data

    # Delete previous reaction
    response = client.post("/1/1/reaction")
    assert b"deleted" in response.data

    # Invalid values
    response = client.post("/5/1/reaction")
    assert b"Invalid reaction" in response.data

    response = client.post("/0/55/reaction")
    assert b"Invalid post" in response.data

    # Insert net post
    with app.app_context():
        db = get_db()
        db.execute(
            "INSERT INTO post (title, body, author_id, created) VALUES ('test title2', 'test2' || x'0a' || 'body', 1, '2018-01-01 00:00:00')"
        )
        db.commit()

    response = client.post("/0/2/reaction")
    assert b"registered" in response.data
