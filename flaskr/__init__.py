import os
from flask import Flask


# create and configure the app
def create_app(test_config=None):  # factory function
    app = Flask(
        __name__, instance_relative_config=True
    )  # config files are relative to instance folder
    app.config.from_mapping(
        SECRET_KEY="dev",  # Temporary, should be stored in env var
        DATABASE=os.path.join(
            app.instance_path, "flaskr.sqlite"
        ),  # path to sqlite database file
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile(
            "config.py", silent=True
        )  # can be used to set the secret key
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(
            app.instance_path
        )  # creates the instance folder if does not exists, will be storing the database file
    except OSError:
        pass

    # test page
    @app.route("/hello")
    def hello():
        return "hello"

    # import the db file from the same directory
    # init app set up the close_db function to be called after every http request and adds the cli command to the flask application
    from . import db

    db.init_app(app)

    # Blueprints
    from . import auth

    app.register_blueprint(auth.bp)

    from . import blog

    app.register_blueprint(blog.bp)

    app.add_url_rule("/", endpoint="index")

    return app
