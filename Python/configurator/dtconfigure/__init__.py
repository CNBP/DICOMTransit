import os

from flask import Flask
from Python.PythonUtils.file import full_file_path
from Python.PythonUtils.folder import get_abspath


path_current_script = full_file_path(__file__)
path_project = get_abspath(path_current_script, 3)
os.chdir(path_project)

def create_app(test_config=None):
    """
    Create and configure the app
    :param test_config:
    :return:
    """

    path_localDB = os.path.join(path_project, "LocalDB")

    app = Flask(__name__, instance_relative_config=True, instance_path=path_localDB)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'dtconfigure.sqlite'),
    )
    print(os.path.join(app.instance_path, 'dtconfigure.sqlite'))

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
