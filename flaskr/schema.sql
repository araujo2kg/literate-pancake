DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS post;
DROP TABLE IF EXISTS reactions;
DROP TABLE IF EXISTS comments;
DROP VIEW IF EXISTS post_info;

CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE post (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    author_id INTEGER NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    FOREIGN KEY (author_id) REFERENCES user (id)
);

-- 0 == Like, 1 == Dislike
CREATE TABLE reactions (
    user_id INTEGER NOT NULL,
    post_id INTEGER NOT NULL,
    reaction INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user (id),
    FOREIGN KEY (post_id) REFERENCES post (id),
    PRIMARY KEY (user_id, post_id),
    CHECK (reaction in (0, 1))
);


CREATE TABLE comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    post_id INTEGER NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    body TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user (id),
    FOREIGN KEY (post_id) REFERENCES post (id),
);


CREATE VIEW post_info AS
SELECT post.id, post.author_id, post.created, post.title, post.body, user.username,
(SELECT COUNT(reaction) FROM reactions WHERE post_id = post.id AND reaction = 0) as likes,
(SELECT COUNT(reaction) FROM reactions WHERE post_id = post.id AND reaction = 1) as dislikes
FROM post JOIN user ON post.author_id = user.id
ORDER BY created DESC;
