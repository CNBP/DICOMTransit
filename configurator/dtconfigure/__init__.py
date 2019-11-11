import os, sys

from flask import Flask

from pathlib import Path


path_file = os.path.dirname(os.path.realpath(__file__))
path_module = Path(path_file)
sys.path.append(f"{path_module}")


def create_app(test_config=None):

    path_current_file = Path(__file__)
    path_project = path_current_file.parents[3]
    path_LocalDB = path_project.joinpath("LocalDB")
    string_LocalDB = str(path_LocalDB.joinpath("dtconfigure.sqlite"))

    print(string_LocalDB)

    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(SECRET_KEY="dev", DATABASE=string_LocalDB)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route("/hello")
    def hello():
        return "Hello, World!"

    # import and register the functions to setup the app db
    import configurator.dtconfigure.db

    configurator.dtconfigure.db.init_app(app)

    # import and register the auth blueprint
    import configurator.dtconfigure.auth

    app.register_blueprint(configurator.dtconfigure.auth.bp)

    # import and register the configure blueprint
    import configurator.dtconfigure.configure

    app.register_blueprint(configurator.dtconfigure.configure.bp)
    app.add_url_rule("/", endpoint="index")

    return app
