def test_rss(client, auth):
    # Create post without image to assert default image is inserted
    auth.login()
    client.post(
        "/create", data={"title": "no image", "body": "testing", "tags": ""}
    )
    response = client.get("/rss")
    assert response.status_code == 200
    assert response.content_type == "application/rss+xml"
    assert b"<?xml" in response.data
    assert b"<rss" in response.data
    assert b"<title>Flaskr</title>" in response.data
    assert b"<title>test title</title>" in response.data
    assert b"<title>no image</title>" in response.data
