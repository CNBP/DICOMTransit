import os

from flask import Flask

from pathlib import Path

def create_app(test_config=None):

    path_current_file = os.path.abspath(__file__)
    path_project = Path(path_current_file).parents[3]
    path_LocalDB = path_project.joinpath("LocalDB")
    string_LocalDB = path_LocalDB.joinpath('dtconfigure.sqlite').resolve().as_posix()

    print(string_LocalDB)

    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=string_LocalDB,
    )


    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    # import and register the functions to setup the app db
    from . import db
    db.init_app(app)

    # import and register the auth blueprint
    from . import auth
    app.register_blueprint(auth.bp)

    # import and register the configure blueprint
    from . import configure
    app.register_blueprint(configure.bp)
    app.add_url_rule('/', endpoint='index')


    return app
