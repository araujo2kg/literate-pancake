from flaskr.tag import treat_tags, create_tags, link_tags, get_tags, remove_tags
from flaskr.db import get_db


def test_treat_tags():
    input = [{"value": "Tag1"}, {"value": "Tag2"}]
    output = [{"value": "tag1"}, {"value": "tag2"}]
    assert treat_tags(input) == output


def test_create_tags(app):
    input = [{"value": "tag1"}, {"value": "tag2"}, {"value": "tagname"}]
    with app.app_context():
        create_tags(input)
        db = get_db()
        count = db.execute("SELECT COUNT(id) FROM tag WHERE name = 'tag1' OR name = 'tag2'").fetchone()[0]
        assert count == 2


def test_link_tags(app):
    input = [{"value": "tag1"}, {"value": "tag2"}]
    with app.app_context():
        create_tags(input)
        link_tags(1, input)
        db = get_db()
        count = db.execute("SELECT COUNT(post_id) FROM posts_tags WHERE tag_id = 2 OR tag_id = 3").fetchone()[0]
        assert count == 2

        # Invalid post case
        error = link_tags(666, input)
        assert error == "Invalid post."

    
def test_get_tags(app):
    with app.app_context():
        tags = get_tags(1)
        assert tags == ["tagname"]


def test_remove_tags(app):
    with app.app_context():
        remove_tags(1)
        db = get_db()
        count = db.execute("SELECT COUNT(post_id) FROM posts_tags WHERE post_id = 1").fetchone()[0]
        assert count == 0

        
def test_posts_by_tag(client, auth, app):
    response = client.get("/tag/tagname/")
    assert response.status_code == 200
    assert b"#tagname" in response.data
    assert b'href="/tag/tagname/"' in response.data
    assert b'href="/1/update"' not in response.data
    auth.login()
    response = client.get("/tag/tagname/")
    assert b'href="/1/update"' in response.data

    # Tag does not exist 
    response = client.get("/tag/none/")
    assert b"Tag (none) not found." in response.data

    # Tag exists but there are not posts with it
    with app.app_context():
        db = get_db()
        client.post("/1/delete")
        response = client.get("/tag/tagname/")
        assert b"No posts found for tag" in response.data
    
    
    