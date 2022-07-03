from flask import Flask
from flask_bootstrap import Bootstrap

from nav import nav
from routes import frontend
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect()
server = Flask(__name__)
csrf.init_app(server)

Bootstrap(server)

server.register_blueprint(frontend)

# Because we're security-conscious developers, we also hard-code disabling
# the CDN support (this might become a default in later versions):
server.config["BOOTSTRAP_SERVE_LOCAL"] = True
server.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
server.config['UPLOAD_FOLDER'] = '/deploy/import_export_data/'
server.config['DB_HOSTNAME'] = 'db_server'

server.config.update(dict(
    SECRET_KEY="powerful secretkey",
    WTF_CSRF_SECRET_KEY="a csrf secret key"
))

# We initialize the navigation as well
nav.init_app(server)
