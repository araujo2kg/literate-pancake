from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort
from flaskr.auth import login_required
from flaskr.db import get_db
import sqlite3

bp = Blueprint("blog", __name__)


@bp.route("/")
def index():
    db = get_db()
    posts = db.execute("SELECT * FROM post_info").fetchall()

    # If user is logged, return their likes and dislikes too
    if g.user:
        db = get_db()
        reactions = db.execute(
            "SELECT post_id, reaction FROM reactions WHERE user_id = ?", (g.user["id"],)
        )
        # Turn it into a dict for easy access in the like/dislike buttons
        reactions_dict = {
            reaction["post_id"]: reaction["reaction"] for reaction in reactions
        }
        return render_template("blog/index.html", posts=posts, reactions=reactions_dict)

    return render_template("blog/index.html", posts=posts)


@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "INSERT INTO post (title, body, author_id)" " VALUES (?, ?, ?)",
                (title, body, g.user["id"]),
            )
            db.commit()
            return redirect(url_for("blog.index"))

    return render_template("blog/create.html")


# the check author parameter it useful if we want to get a post, but we don't care if the user is the author
def get_post(id, check_author=True):
    post = (
        get_db()
        .execute(
            "SELECT p.id, title, body, created, author_id, username"
            " FROM post p JOIN user u ON p.author_id = u.id"
            " WHERE p.id = ?",
            (id,),
        )
        .fetchone()
    )

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post["author_id"] != g.user["id"]:
        abort(403)

    return post


# To redirect users to the update view correctly, the id of the post needs to be passed with url_for function
# Ex: url_for('blog.update', id=post['id'])
@bp.route("/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    # The get_post check if the user is the author of the post
    post = get_post(id)

    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "UPDATE post SET title = ?, body = ?" " WHERE id= ?", (title, body, id)
            )
            db.commit()
            return redirect(url_for("blog.index"))

    return render_template("blog/update.html", post=post)


@bp.route("/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    # Get post checks if the logged user is the author
    get_post(id)
    db = get_db()
    db.execute("DELETE FROM post WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for("blog.index"))


@bp.route("/<int:id>/post", methods=("GET",))
def post(id):
    # get_post checks if logged in user is the author by default, so we need to pass the false as arg
    post = get_post(id, check_author=False)

    return render_template("blog/post.html", post=post)


@bp.route("/<int:reaction>/<int:post_id>/reaction", methods=("POST",))
@login_required
def reaction(reaction, post_id):
    # 0 = like, 1 = dislike
    if reaction not in (0, 1):
        abort(404, "Invalid operation")

    db = get_db()
    try:
        db.execute(
            "INSERT INTO reactions (user_id, post_id, reaction) VALUES (?, ?, ?)",
            (g.user["id"], post_id, reaction),
        )
        db.commit()
        return "Reaction registered."

    except sqlite3.IntegrityError:
        # If post does not exist
        if db.execute("SELECT * FROM post WHERE id = ?", (post_id,)).fetchone() == None:
            abort(404, "Invalid operation")

        # Get existing reaction
        old_reaction = db.execute(
            "SELECT reaction FROM reactions WHERE user_id = ? AND post_id = ?",
            (g.user["id"], post_id),
        ).fetchone()
        old_reaction = old_reaction["reaction"]

        # If reaction is the same as existing, remove the reaction
        if old_reaction == reaction:
            db.execute(
                "DELETE FROM reactions WHERE user_id = ? AND post_id = ? AND reaction = ?",
                (g.user["id"], post_id, reaction),
            )
            db.commit()
            return "Reaction deleted."

        # If reaction is different, update
        if old_reaction != reaction:
            db.execute(
                "UPDATE reactions SET reaction = ? WHERE user_id = ? AND post_id = ?",
                (reaction, g.user["id"], post_id),
            )
            db.commit()
        return "Reaction updated."
