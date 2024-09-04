from flaskr.db import get_db
from flaskr.comments import get_comments


def test_create(app, auth, client):
    result = client.post("/comments/create")
    assert result.headers["Location"] == "/auth/login"
    assert result.status_code == 302

    auth.login()
    result = client.post(
        "/comments/create", data={"user_id": 1, "post_id": 1, "body": ""}
    )
    assert b"Comment is too short!" in result.data

    result = client.post(
        "/comments/create",
        data={"user_id": 1, "post_id": 1, "body": "second comment"},
    )
    assert result.headers["Location"] == "/1/post"

    result = client.post(
        "/comments/create",
        data={"user_id": 1, "post_id": 666, "body": "second comment"},
    )
    assert b"Invalid post." in result.data

    # Assert that the comment was created
    with app.app_context():
        db = get_db()
        comment = db.execute("SELECT COUNT(id) FROM comments").fetchone()[0]
        assert comment == 2


def test_get_comments(app):
    with app.app_context():
        # Receives comment id
        comment = get_comments(1)
        assert comment[0]["username"] == "test"
        assert comment[0]["id"] == 1

        comment = get_comments(666)
        assert comment is None


def test_update(auth, client, app):
    response = client.get("/comments/1/update")
    assert response.status_code == 302
    assert response.headers["Location"] == "/auth/login"

    auth.login()
    response = client.get("/comments/1/update")
    assert response.status_code == 200
    assert b"Edit comment" in response.data
    assert b"comment body test" in response.data

    response = client.post("/comments/1/update", data={"body": ""})
    assert b"Comment is too short!" in response.data

    response = client.post("/comments/666/update", data={"body": ""})
    assert b"Comment does not exist." in response.data

    # Succesful update redirects to post where comment was
    response = client.post(
        "/comments/1/update", data={"body": "new comment body"}
    )
    assert response.status_code == 302
    assert response.headers["Location"] == "/1/post"

    # Asserts that user cannot update another person comment
    with app.app_context():
        db = get_db()
        # Create comment with secondary test user (other, id=2)
        db.execute(
            "INSERT INTO comments (user_id, post_id, body) VALUES (2, 1, 'other comment')"
        )
        db.commit()
        # Try to update other user comment
        response = client.post(
            "/comments/2/update", data={"body": "updating comment"}
        )
        assert b"Forbidden" in response.data


def test_delete(client, auth, app):
    response = client.post("/comments/1/delete")
    assert response.status_code == 302
    assert response.headers["Location"] == "/auth/login"

    auth.login()
    response = client.post("/comments/666/delete")
    assert b"Comment not found." in response.data

    with app.app_context():
        # After deletion it redirects to the post where the comments resided
        response = client.post("/comments/1/delete")
        assert response.status_code == 302
        assert response.headers["Location"] == "/1/post"

        # Asserts that user cannot delete another person comment
        db = get_db()
        # Create comment with secondary test user (other, id=2)
        db.execute(
            "INSERT INTO comments (user_id, post_id, body) VALUES (2, 1, 'other comment')"
        )
        db.commit()

        response = client.post("/comments/2/delete")
        assert b"Forbidden" in response.data
