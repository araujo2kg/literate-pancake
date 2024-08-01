from flask import Blueprint, g, redirect, request, url_for, render_template
from werkzeug.exceptions import abort
from flaskr.db import get_db
from flaskr.auth import login_required
import sqlite3

bp = Blueprint("comments", __name__, url_prefix="/comments")


@bp.route("/create", methods=("POST",))
@login_required
def create():
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
            (user_id, post_id, body),
        )
        db.commit()
        return "Comment registered."

    except sqlite3.IntegrityError:
        return "Invalid post."


def get_comments(post):
    db = get_db()
    comments = db.execute(
        "SELECT comments.id, user_id, post_id, created, body, user.username"
        " FROM comments JOIN user ON user_id = user.id"
        " WHERE post_id = ?",
        (post,),
    ).fetchall()

    if not comments:
        return None

    return comments


@bp.route("/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    db = get_db()
    comment = db.execute("SELECT * FROM comments WHERE id = ?", (id,)).fetchone()

    if comment is None:
        return "Comment does not exist."

    if g.user["id"] != comment["user_id"]:
        return "Forbidden"

    if request.method == "POST":
        body = request.form.get("body")
        error = None

        if not body or len(body) < 2:
            error = "Comment is too short!"

        if error is not None:
            return error

        db = get_db()
        db.execute("UPDATE comments SET body = ? WHERE id = ?", (body, id))
        db.commit()
        return redirect(url_for("blog.post", id=comment["post_id"]))

    return render_template("comments/update.html", comment=comment)


@bp.route("/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    db = get_db()
    comment = db.execute("SELECT * FROM comments WHERE id = ?", (id,)).fetchone()

    if comment is None:
        return abort(404, "Comment not found.")

    if g.user["id"] != comment["user_id"]:
        return "Forbidden"

    # If reactions are added to comments later, reactions need to be deleted first
    db.execute("DELETE FROM comments WHERE id = ?", (id,))
    db.commit()

    return redirect(url_for("blog.post", id=comment["post_id"]))
