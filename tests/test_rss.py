def test_rss(client):
    response = client.get("/rss")
    assert response.status_code == 200
    assert response.content_type == "application/rss+xml"
    assert b"<?xml" in response.data
    assert b"<rss" in response.data
    assert b"<title>Flaskr</title>" in response.data
    assert b"<title>test title</title>" in response.data
