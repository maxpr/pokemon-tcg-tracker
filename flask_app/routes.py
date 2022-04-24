# This contains our frontend; since it is a bit messy to use the @app.route
# decorator style when using application factories, all of our routes are
# inside blueprints. This is the front-facing blueprint.
#
# You can find out more about blueprints at
# http://flask.pocoo.org/docs/blueprints/
from clickhouse_driver import Client
from flask import Blueprint, render_template, flash, redirect, url_for
from flask_nav.elements import Navbar, View, Subgroup, Link, Text, Separator
from pokemon_data_scraper.src.logger.logging import LOGGER
from nav import nav


frontend = Blueprint('frontend', __name__)

# We're adding a navbar as well through flask-navbar. In our example, the
# navbar has an usual amount of Link-Elements, more commonly you will have a
# lot more View instances.
nav.register_element('frontend_top', Navbar(
    View('Flask-Bootstrap', '.index'),
    View('Home', '.index'),
    View('Extensions', '.extensions_list')))


@frontend.route('/')
def index():
    return render_template('index.html')


# TODO: have extensions in table sorted by release date
@frontend.route('/extensions')
def extensions_list():
    client = Client('db_server')
    return render_template('extensions_list.html', extensions_df=client.query_dataframe(f"SELECT extensionName, extensionCode, extensionImageUrl, extensionCardNumber, toDate(extensionReleaseDate) FROM pokemon.extensions ORDER BY extensionReleaseDate DESCENDING"))


# TODO: have extensions in table sorted by release date
@frontend.route('/extension/<code>')
def extension_details(code):
    client = Client('db_server')
    return render_template('extension_details.html', ext=client.query_dataframe(f"SELECT cardName, cardImageUrl, cardNumber  FROM pokemon.cardList WHERE cardExtensionCode='{code}' ORDER BY cardNumber ASCENDING"))


@frontend.route('/data_post', methods=['POST'])
def data_post():
    # handle your database access, etc.
    LOGGER.info("TOTOA")
    return 'received'
