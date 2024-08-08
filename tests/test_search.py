def test_search(client, auth):
    response = client.get("/search?q=test")
    assert response.status_code == 200
    assert b"test title" in response.data

    # If search is returning the reactions correctly
    auth.login()
    response = client.get("/search?q=test")
    assert b"activated-like" in response.data

    
