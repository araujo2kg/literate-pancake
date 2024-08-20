from flask import Blueprint, request, g, render_template
from flaskr.db import get_db
from flaskr.pagination import Pagination


bp = Blueprint("search", __name__)


@bp.route("/search", methods=("GET",))
def search():
    page = request.args.get("page", 1, type=int)
    query = request.args.get("q")
    try:
        query = "%" + query + "%"
    except TypeError:
        query = "%"
    db = get_db()
    total_items = db.execute(
        "SELECT COUNT(id) FROM post_info WHERE title LIKE ? OR username LIKE ?",
        (query, query),
    ).fetchone()[0]
    pagination = Pagination(page=page, total_items=total_items)

    posts = db.execute(
        "SELECT * FROM post_info WHERE title LIKE ? OR username LIKE ? LIMIT ? OFFSET ?",
        (query, query, pagination.per_page, pagination.offset),
    ).fetchall()

    # Get user reacions if logged in
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
            endpoint="search.search",
            q=request.args.get("q"),
        )

    return render_template(
        "blog/index.html",
        posts=posts,
        page=page,
        total_pages=pagination.total_pages,
        endpoint="search.search",
        q=request.args.get("q"),
    )
