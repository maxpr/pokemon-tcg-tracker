from flask import Flask
from flask_appconfig import AppConfig
from flask_bootstrap import Bootstrap

from routes import frontend
from nav import nav

server = Flask(__name__)

# We use Flask-Appconfig here, but this is not a requirement
AppConfig(server)

Bootstrap(server)

server.register_blueprint(frontend)

# Because we're security-conscious developers, we also hard-code disabling
# the CDN support (this might become a default in later versions):
server.config['BOOTSTRAP_SERVE_LOCAL'] = True
server.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# We initialize the navigation as well
nav.init_app(server)