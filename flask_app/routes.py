# This contains our frontend; since it is a bit messy to use the @app.route
# decorator style when using application factories, all of our routes are
# inside blueprints. This is the front-facing blueprint.
#
# You can find out more about blueprints at
# http://flask.pocoo.org/docs/blueprints/

from flask import Blueprint, render_template, flash, redirect, url_for
from flask_bootstrap import __version__ as FLASK_BOOTSTRAP_VERSION
from flask_nav.elements import Navbar, View, Subgroup, Link, Text, Separator
from markupsafe import escape

from nav import nav
from os import listdir
from os.path import isfile, join

import pandas as pd

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
    return render_template('extensions_list.html', extensions_list=[f.replace('.csv','') for f in listdir('dummy_data') if isfile(join("dummy_data", f))])


# TODO: have extensions in table sorted by release date
@frontend.route('/extension/<name>')
def extension_details(name):
    print(name+".csv")
    return render_template('extension_details.html', ext=pd.read_csv(f"dummy_data/{name}.csv"))

@frontend.route('/data_post', methods=['POST'])
def data_post():
    # handle your database access, etc.
    print("TOTOA")
    return 'received'
