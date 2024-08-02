from flask import Blueprint, g, redirect, request, url_for, render_template
from werkzeug.exceptions import abort
from flaskr.db import get_db
from flaskr.auth import login_required
import sqlite3

bp = Blueprint("tag", __name__, url_prefix="/tag")


def treat_tags(tags):
    for tag in tags:
        tag["value"] = tag["value"].lower()
    return tags


def create_tags(tags):
    db = get_db()
    for tag in tags:
        result = db.execute("SELECT id FROM tag WHERE name = ?", (tag["value"],)).fetchone()
        if result is None:
            db.execute("INSERT INTO tag (name) VALUES (?)", (tag["value"],))

            
def link_tags(post_id, tags):
    # get the tags ids and insert in the junction table
    db = get_db()
    # Make sure the post exist
    if db.execute("SELECT * FROM post WHERE id = ?", (post_id,)).fetchone() is None:
        return "Invalid post."
    for tag in tags:
        # Get tags ids
        tag["value"] = db.execute("SELECT id FROM tag WHERE name = ?", (tag["value"],)).fetchone()[0]
        # Insert in the junction table
        db.execute("INSERT INTO posts_tags (post_id, tag_id) VALUES (?, ?)", (post_id, tag["value"]))

        
def get_tags(post_id):
    db = get_db()
    tags = db.execute(
        "SELECT name FROM tag WHERE id IN (SELECT tag_id FROM posts_tags WHERE post_id = ?)", (post_id,)
    ).fetchall()
    return tags
    
