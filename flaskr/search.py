from flask import Blueprint, request, g, render_template
from flaskr.db import get_db


bp = Blueprint("search", __name__)

@bp.route("/search", methods=("GET",))
def search():
    query = request.args.get("q")
    query = "%" + query + "%"
    db = get_db()
    posts = db.execute(
        "SELECT * FROM post_info WHERE title LIKE ? OR username LIKE ?", (query, query)
    ).fetchall()

    # Get user reacions if logged in
    if g.user:
        reactions = db.execute(
            "SELECT post_id, reaction FROM reactions WHERE user_id = ?", (g.user["id"],)
        )
        reactions_dict = {
            reaction["post_id"]: reaction["reaction"] for reaction in reactions
        }
        return render_template("blog/index.html", posts=posts, reactions=reactions_dict)

    return render_template("blog/index.html", posts=posts)
