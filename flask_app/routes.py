# This contains our frontend; since it is a bit messy to use the @app.route
# decorator style when using application factories, all of our routes are
# inside blueprints. This is the front-facing blueprint.
#
# You can find out more about blueprints at
# http://flask.pocoo.org/docs/blueprints/
import time
from datetime import datetime

from clickhouse_driver import Client
from flask import Blueprint, render_template, Response
from flask_nav.elements import Navbar, View

from pokemon_data_scraper.src.db.db_connector import DBHandler
from pokemon_data_scraper.src.logger.logging import LOGGER
from nav import nav
from flask import request
from pokemon_data_scraper.src.scraping.scrap_extensions import main_computation

frontend = Blueprint('frontend', __name__)

# We're adding a navbar as well through flask-navbar. In our example, the
# navbar has an usual amount of Link-Elements, more commonly you will have a
# lot more View instances.
nav.register_element('frontend_top',
    Navbar(
        View('Home', '.index'),
        View('Extensions', '.extensions_list'),
        View('Options', '.options')
    )
)


@frontend.route('/')
def index():
    return render_template('index.html')


# TODO: extensions progress
@frontend.route('/extensions')
def extensions_list():
    client = DBHandler('db_server')
    return render_template('extensions_list.html', extensions_df=client.get_all_extensions_for_ui())


@frontend.route('/extension/<name_code>')
def extension_details(name_code: str):
    client = DBHandler('db_server')
    return render_template('extension_details.html', ext_name=name_code.split("_")[1], ext_code=name_code.split("_")[0], ext=client.get_card_list_for_extension(name_code.split("_")[0]))


@frontend.route('/data_post', methods=['POST'])
def data_post():
    # handle your database access, etc.
    LOGGER.debug(f"Request is {request.json}")
    client = DBHandler('db_server')
    client.insert_owned_card(request.json)
    return 'received'


@frontend.route('/options')
def options():
    return render_template('options.html')


@frontend.route("/log_stream", methods=["GET"])
def log_stream():
    """returns logging information"""
    def generate():
        with open('/deploy/flask_app/logs/scrapping_worker.log') as f:
            while True:
                yield f.read()
                time.sleep(1)
    return Response(generate(), mimetype="text/plain", content_type="text/event-stream")


@frontend.route('/fetch_extensions', methods=['POST'])
def launch_fetching_extensions():
    LOGGER.info("We are starting to fetch extensions")
    main_computation()
    return ''
