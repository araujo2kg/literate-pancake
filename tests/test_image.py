from flaskr.image import create_image_name, save_image, delete_image, create_image_connection
from flaskr.db import get_db
from werkzeug.datastructures import FileStorage
import os


def test_get_image(client):
    response = client.get("/image/test.png")
    assert response.status_code == 200
    assert response.content_type == "image/png"

    response = client.get("/image/666.png")
    assert response.status_code == 404


def test_create_image_name(setup_image):
    imagename = create_image_name(setup_image)
    assert imagename is not None
    assert imagename.endswith(".png")

    # Invalid content_type
    error_test = create_image_name(FileStorage(filename="test.txt", content_type="text/plain"))
    assert error_test is None

    
def test_save_image(app, setup_image, client):
    with app.app_context():
        save_image(setup_image, "test_save.png")
        response = client.get("image/test_save.png")
        assert response.content_type == "image/png"

    
def test_delete_image(app):
    image_path = os.path.join(app.config["IMAGES_DIR"], "test.png")
    with app.app_context():
        assert os.path.exists(image_path) == True
        delete_image("test.png")
        assert os.path.exists(image_path) == False
        # No image
        response = delete_image("no_image")
        assert response == 1
    

def test_create_image_connection(app):
    with app.app_context():
        # Delete previous connections from test post
        db = get_db()
        db.execute("DELETE FROM post_image WHERE post_id = 1")
        create_image_connection(post_id=1, imagename="test")
        result = db.execute("SELECT * FROM post_image WHERE post_id = 1").fetchone()
        assert result["post_id"] == 1
        assert result["imagename"] == "test"