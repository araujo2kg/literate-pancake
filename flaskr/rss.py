from flask import Blueprint, Response
from feedgen.feed import FeedGenerator
from flaskr.db import get_db

bp = Blueprint("rss", __name__)


@bp.route("/rss", methods=("GET",))
def rss():
    db = get_db()
    posts = db.execute("SELECT * FROM post_info LIMIT 5").fetchall()
    print(posts)

    fg = FeedGenerator()
    fg.title("Flaskr")
    fg.description("Your daily dose of suffering!")
    fg.link(href="http://127.0.0.1:5000/")

    for post in posts:
        fe = fg.add_entry()
        fe.title(post["title"])
        fe.description(post["body"][:100])
        fe.link(href=f"http://127.0.0.1:5000/{post['id']}/post")

    rss_feed = fg.rss_str(pretty=True)
    response = Response(rss_feed, content_type="application/rss+xml")
    return response

