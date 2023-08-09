import os
import sys
from flask import Flask


# creates the Application Factory where you are moving the creation of the application object into a function
# multiple instances of this app can then be created later

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)    # the instance folder is located outside the flaskr package
    # the instance folder designed to not be under version control and be deployment specific, good for things that change at runtime or configuration files
    # behavior of relative paths in the config files can be flipped between "relative to the application root" (default) to "relative to instance folder"
    
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
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
        print("What Prefix is set to: ")
        print(sys.prefix)
        return 'Hello, World!'
    
    # Register the Database with the application
    from . import db
    db.init_app(app)

    # Import and register the 'auth' blueprint from the factory
    from . import auth
    app.register_blueprint(auth.bp)

    # Import and register the 'blog' blueprint from the factory
    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint = 'index')

    return app