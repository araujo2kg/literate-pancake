from flask import Blueprint, send_from_directory, current_app
from flaskr.db import get_db
import os
import uuid


bp = Blueprint("image", __name__, url_prefix="/image")


@bp.route("/<imagename>", methods=["GET"])
def get_image(imagename):
    return send_from_directory(
        current_app.config["IMAGES_DIR"], imagename, as_attachment=False
    )


def create_image_name(image):
    if image.content_type not in ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/bmp', 'image/webp', 'image/avif']:
        return None
    imagename = image.filename
    extension = os.path.splitext(imagename)[1]
    imagename = f"{uuid.uuid4()}{extension}"
    return imagename


def save_image(image, imagename):
    image.save(os.path.join(current_app.config["IMAGES_DIR"], imagename))

def delete_image(imagename):
    if imagename == "no_image":
        return 1
    os.remove(os.path.join(current_app.config["IMAGES_DIR"], imagename))

def create_image_connection(post_id, imagename):
    db = get_db()
    db.execute("INSERT INTO post_image (post_id, imagename) VALUES (?, ?)", (post_id, imagename))
    db.commit()
