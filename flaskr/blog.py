from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    url_for,
    current_app
)
from werkzeug.exceptions import abort
from flaskr.auth import login_required
from flaskr.db import get_db
from flaskr.comments import get_comments
from flaskr.tag import treat_tags, create_tags, link_tags, get_tags, remove_tags
from flaskr.pagination import Pagination
from flaskr.image import create_image_name, save_image, delete_image, create_image_connection
import json
import sqlite3
import os

bp = Blueprint("blog", __name__)


@bp.route("/")
def index():
    page = request.args.get("page", 1, type=int)
    db = get_db()
    total_items = db.execute("SELECT COUNT(id) FROM post_info").fetchone()[0]
    pagination = Pagination(total_items=total_items, page=page)

    posts = db.execute(
        "SELECT * FROM post_info LIMIT ? OFFSET ?",
        (pagination.per_page, pagination.offset),
    ).fetchall()
    # If user is logged, return their likes and dislikes too
    if g.user:
        reactions = db.execute(
            "SELECT post_id, reaction FROM reactions WHERE user_id = ?",
            (g.user["id"],),
        )
        reactions_dict = {
            reaction["post_id"]: reaction["reaction"] for reaction in reactions
        }
        return render_template(
            "blog/index.html",
            posts=posts,
            reactions=reactions_dict,
            page=page,
            total_pages=pagination.total_pages,
            endpoint="blog.index",
            q=request.args.get("q"),
        )

    return render_template(
        "blog/index.html",
        posts=posts,
        page=page,
        total_pages=pagination.total_pages,
        endpoint="blog.index",
        q=request.args.get("q"),
    )


@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        image = request.files.get("image")
        error = None

        # Tagify returns json string
        tags = request.form.get("tags")
        try:
            tags = json.loads(tags)
            # Lowercase, remove white-spaces etc.
            tags = treat_tags(tags)
            # Add tags to database if they still do not exist
            create_tags(tags)
        # In case no tags were passed
        except json.JSONDecodeError:
            tags = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            result = db.execute(
                "INSERT INTO post (title, body, author_id)" " VALUES (?, ?, ?)",
                (title, body, g.user["id"]),
            )
            post_id = result.lastrowid
            # If tags were provided, insert in the junction table
            if tags is not None:
                link_tags(post_id, tags)
            # If image was provided, save it and insert in the junction table
            if image:
                # If file is not image, returns none
                imagename = create_image_name(image)
                if imagename is not None:
                    save_image(image, imagename)
                    create_image_connection(post_id, imagename)
                    
                
            db.commit()
            return redirect(url_for("blog.index"))

    return render_template("blog/create.html")


# the check author parameter it useful if we want to get a post, but we don't care if the user is the author
def get_post(id, check_author=True):
    post = (
        get_db()
        .execute(
            "SELECT p.id, title, body, created, author_id, username,"
            "(SELECT COUNT(reaction) FROM reactions WHERE post_id = ? AND reaction = 0) as likes,"
            "(SELECT COUNT(reaction) FROM reactions WHERE post_id = ? AND reaction = 1) as dislikes"
            " FROM post p JOIN user u ON p.author_id = u.id"
            " WHERE p.id = ?",
            (id, id, id),
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
    db = get_db()
    post = db.execute("SELECT * FROM post_info WHERE id = ?", (id,)).fetchone()

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")
    if post["author_id"] != g.user["id"]:
        abort(403)

    tags = get_tags(id)
    current_image = db.execute("SELECT * FROM post_image WHERE post_id = ?", (id,)).fetchone()

    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        error = None
        # If blank, returns an empty fileobject
        new_image = request.files.get("image")

        # Tagify tags in json format
        tags = request.form.get("tags")
        try:
            tags = json.loads(tags)
            tags = treat_tags(tags)
            create_tags(tags)
        except json.JSONDecodeError:
            tags = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            # Update post
            db.execute(
                "UPDATE post SET title = ?, body = ?" " WHERE id= ?",
                (title, body, id),
            )
            # Remove previous tags
            remove_tags(id)
            # Update tags
            if tags is not None:
                link_tags(id, tags)
            # Update image
            if new_image and new_image.filename != '':
                # Add new image to folder
                imagename = create_image_name(new_image)
                save_image(new_image, imagename)
                # Update
                if current_image is not None:
                    # Delete current image from folder
                    delete_image(current_image["imagename"])
                    # Update the connection
                    db.execute("UPDATE post_image SET imagename = ? WHERE imagename = ?", (imagename, current_image["imagename"]))
                # Create
                else:
                    create_image_connection(id, imagename)
            db.commit()
            return redirect(url_for("blog.index"))

    return render_template("blog/update.html", post=post, tags=tags, image=current_image)


@bp.route("/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    # Get post checks if the logged user is the author
    get_post(id)
    imagename = request.form.get("imagename", "no_image")
    db = get_db()
    # Delete all the reactions from the reaction table related to this post
    db.execute("DELETE FROM reactions WHERE post_id = ?", (id,))
    # Delete all the comments
    db.execute("DELETE FROM comments WHERE post_id = ?", (id,))
    # Delete the tags
    db.execute("DELETE FROM posts_tags WHERE post_id = ?", (id,))
    # Delete the image connection and the image file
    db.execute("DELETE FROM post_image WHERE post_id = ?", (id,))
    delete_image(imagename)
    # Delete the post
    db.execute("DELETE FROM post WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for("blog.index"))
    # The order of queries here is important because when foreign key constraints are activated,
    # you cannot deleted some data that has a foreign key pointing to it, to prevent orphaned data


@bp.route("/<int:id>/post", methods=("GET",))
def post(id):
    db = get_db()
    post = db.execute("SELECT * FROM post_info WHERE id = ?", (id,)).fetchone()
    comments = get_comments(id)

    # If user is logged, return their reaction to the post
    if g.user:
        db = get_db()
        reactions = db.execute(
            "SELECT post_id, reaction FROM reactions WHERE user_id = ? AND post_id = ?",
            (g.user["id"], id),
        )
        reaction_dict = {
            reaction["post_id"]: reaction["reaction"] for reaction in reactions
        }
        return render_template(
            "blog/post.html",
            post=post,
            reaction=reaction_dict,
            comments=comments,
        )

    return render_template(
        "blog/post.html", post=post, comments=comments
    )


@bp.route("/<int:reaction>/<int:post_id>/reaction", methods=("POST",))
@login_required
def reaction(reaction, post_id):
    # 0 = like, 1 = dislike
    if reaction not in (0, 1):
        abort(404, "Invalid reaction")

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
        if (
            db.execute("SELECT * FROM post WHERE id = ?", (post_id,)).fetchone()
            == None
        ):
            abort(404, "Invalid post")

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

        # If reaction is different, just update
        db.execute(
            "UPDATE reactions SET reaction = ? WHERE user_id = ? AND post_id = ?",
            (reaction, g.user["id"], post_id),
        )
        db.commit()
        return "Reaction updated."
