from flask import Blueprint, Response
from feedgen.feed import FeedGenerator
from flaskr.db import get_db
import os
import pytz

bp = Blueprint("rss", __name__)


@bp.route("/rss", methods=("GET",))
def rss():
    db = get_db()
    posts = db.execute("SELECT * FROM post_info LIMIT 5").fetchall()

    fg = FeedGenerator()
    fg.title("Flaskr")
    fg.description("Your daily dose of suffering!")
    fg.link(href="http://127.0.0.1:5000/")
    fg.logo("http://127.0.0.1:5000/image/lena.bmp")
    fg.language("en")

    for post in posts:
        fe = fg.add_entry()
        fe.title(post["title"])
        fe.description(post["body"][:100])
        fe.link(href=f"http://127.0.0.1:5000/{post['id']}/post")
        fe.author({"name": post['username'], "email": f"{post['username']}@example.com"})
        fe.published(post["created"].replace(tzinfo=pytz.UTC))
        if post["imagename"]:
            fe.enclosure(url=f"http://127.0.0.1:5000/image/{post['imagename']}", length="500000", type=f"image/{os.path.splitext(post['imagename'])[1][1:]}")
        else: 
            fe.enclosure(url="http://127.0.0.1:5000/image/lena.bmp", length="500000", type="image/bmp")

    rss_feed = fg.rss_str(pretty=True)
    response = Response(rss_feed, content_type="application/rss+xml")
    return response

