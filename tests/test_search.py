def test_search(client, auth):
    response = client.get("/search?q=test")
    assert response.status_code == 200
    assert b"test title" in response.data
    assert b"Page 1 of 1" in response.data

    # If search is returning the reactions correctly
    auth.login()
    response = client.get("/search?q=test")
    assert b"activated-like" in response.data

    # Search with no parameter (none)
    response = client.get("/search")
    assert response.status_code == 200

    
