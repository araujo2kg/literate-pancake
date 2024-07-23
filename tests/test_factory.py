from flaskr import create_app


# Asserts that when create_app is called with the config it correctly runs it (options in factory)
def test_config():
    # testing is boolean indicating if the application is running on test mode or not
    assert not create_app().testing
    assert create_app({'TESTING': True}).testing

    
def test_hello(client):
    response = client.get('/hello')
    # .data attribute contains the http response body as bytes, the b, before the string literal denotes a bytes literal
    # it is necessary to compare to the value in .data
    assert response.data == b'hello'
    