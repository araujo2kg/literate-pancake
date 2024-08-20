from flask import Blueprint, send_from_directory, current_app
from flaskr.db import get_db

bp = Blueprint("image", __name__, url_prefix="/image")


@bp.route("/<imagename>", methods=["GET"])
def get_image(imagename):
    return send_from_directory(
        current_app.config["IMAGES_DIR"], imagename, as_attachment=False
    )
