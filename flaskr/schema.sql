DROP VIEW IF EXISTS post_info;
DROP TABLE IF EXISTS posts_tags;
DROP TABLE IF EXISTS post_image;
DROP TABLE IF EXISTS reactions;
DROP TABLE IF EXISTS comments;
DROP TABLE IF EXISTS tag;
DROP TABLE IF EXISTS post;
DROP TABLE IF EXISTS user;

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
    FOREIGN KEY (post_id) REFERENCES post (id)
);

CREATE TABLE tag (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE posts_tags (
    post_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    FOREIGN KEY (post_id) REFERENCES post (id),
    FOREIGN KEY (tag_id) REFERENCES tag (id),
    PRIMARY KEY (post_id, tag_id)
);

CREATE TABLE post_image (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER NOT NULL,
    imagename TEXT NOT NULL,
    FOREIGN KEY (post_id) REFERENCES post (id)
)

CREATE VIEW post_info AS
SELECT post.id, post.author_id, post.created, post.title, post.body, user.username,
GROUP_CONCAT(tag.name) as tag_names,
(SELECT COUNT(reaction) FROM reactions WHERE post_id = post.id AND reaction = 0) as likes,
(SELECT COUNT(reaction) FROM reactions WHERE post_id = post.id AND reaction = 1) as dislikes
FROM post 
JOIN user ON post.author_id = user.id
LEFT JOIN posts_tags ON post.id = posts_tags.post_id
LEFT JOIN tag ON posts_tags.tag_id = tag.id
GROUP BY post.id
ORDER BY created DESC;
