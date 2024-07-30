from flask import Blueprint, g, redirect, request, url_for
from flaskr.db import get_db
from flaskr.auth import login_required
import sqlite3

bp = Blueprint("comments", __name__, url_prefix="/comments")

@bp.route("/create", methods=("POST",))
@login_required
def comments():
        user_id = g.user["id"]
        post_id = request.form.get("post_id")
        body = request.form.get("body")
        error = None

        if not body or len(body) < 2:
            error = "Comment is too short!"

        if error is not None:
            return error
        try:
            db = get_db()
            db.execute(
                "INSERT INTO comments (user_id, post_id, body) VALUES (?, ?, ?)",
                (user_id, post_id, body)
            )
            db.commit()
            return "Comment registered."

        except sqlite3.IntegrityError:
            return "Invalid post."