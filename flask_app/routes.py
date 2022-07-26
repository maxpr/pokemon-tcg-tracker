# This contains our frontend; since it is a bit messy to use the @app.route
# decorator style when using application factories, all of our routes are
# inside blueprints. This is the front-facing blueprint.
#
# You can find out more about blueprints at
# http://flask.pocoo.org/docs/blueprints/
import time

import pandas as pd
from flask import Blueprint, Response, jsonify, render_template, request, current_app, send_file, flash
from flask_nav.elements import Navbar, View

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import SubmitField

from nav import nav
from pokemon_data_scraper.src.db.db_connector import DBHandler
from pokemon_data_scraper.src.logger.logging import LOGGER
from pokemon_data_scraper.src.scraping.scrap_cards import main_card_fetching
from pokemon_data_scraper.src.scraping.scrap_extensions import main_computation

from werkzeug.utils import secure_filename

frontend = Blueprint("frontend", __name__)


# We're adding a navbar as well through flask-navbar. In our example, the
# navbar has an usual amount of Link-Elements, more commonly you will have a
# lot more View instances.
nav.register_element(
    "frontend_top",
    Navbar(View("Home", ".index"), View("Extensions", ".extensions_list"), View("All cards", ".cards_list"),
           View("Options", ".options")),
)


class UploadForm(FlaskForm):
    validators = [
        FileRequired(message='There was no file!'),
        FileAllowed(['csv'], message='Must be a csv file!')
    ]

    input_file = FileField('', validators=validators)
    submit = SubmitField(label="Upload")


@frontend.route("/")
def index():
    return render_template("index.html")


@frontend.route("/extensions")
def extensions_list():
    return render_template("extension_page.html")


@frontend.route("/cards")
def cards_list():
    return render_template("card_page.html")


@frontend.route("/extension/<name_code>")
def extension_details(name_code: str):
    client = DBHandler(current_app.config['DB_HOSTNAME'])
    return render_template(
        "extension_details.html",
        ext_name=name_code.split("_")[1],
        ext_code=name_code.split("_")[0],
        ext=client.get_card_list_for_extension(name_code.split("_")[0]),
    )


@frontend.route("/data_post", methods=["POST"])
def data_post():
    # handle your database access, etc.
    LOGGER.debug(f"Request is {request.json}")
    client = DBHandler(current_app.config['DB_HOSTNAME'])
    client.insert_owned_card(request.json)
    return "received"


@frontend.route("/options")
def options():
    return render_template("options.html", form = UploadForm())


@frontend.route("/log_extensions_stream", methods=["GET"])
def log_extensions_stream():
    """returns logging information"""

    def generate_log_extensions():
        with open("/deploy/flask_app/logs/logger-extensions-scraper.log") as f:
            while True:
                yield f.read()
                time.sleep(1)

    return Response(generate_log_extensions(), mimetype="text/plain", content_type="text/event-stream")


@frontend.route("/fetch_extensions", methods=["POST"])
def launch_fetching_extensions():
    LOGGER.info("We are starting to fetch extensions")
    main_computation()
    return ""


@frontend.route("/log_cards_stream", methods=["GET"])
def log_cards_stream():
    """returns logging information"""

    def generate_log_cards():
        with open("/deploy/flask_app/logs/logger-cards-scraper.log") as f:
            while True:
                yield f.read()
                time.sleep(1)

    return Response(generate_log_cards(), mimetype="text/plain", content_type="text/event-stream")


@frontend.route("/fetch_cards", methods=["POST"])
def launch_fetching_cards():
    LOGGER.info("We are starting to fetch cards")
    main_card_fetching()
    return ""


@frontend.route("/delete_ext", methods=["POST"])
def delete_ext():
    # handle your database access, etc.
    LOGGER.debug(f"Request is {request.json}")
    client = DBHandler(current_app.config['DB_HOSTNAME'])
    client.delete_extension(request.json)
    return "received"


@frontend.route("/extension_live_search", methods=["POST", "GET"])
def extension_live_search():
    client = DBHandler(current_app.config['DB_HOSTNAME'])
    if request.method == "POST":
        if request.form:
            search_word = request.form["query"]
            LOGGER.info(search_word)
            extensions_list = client.get_all_extensions_for_ui(value=search_word)
        else:
            extensions_list = client.get_all_extensions_for_ui(value="")

    return jsonify({"htmlresponse": render_template("extensions_list.html", extensions_df=extensions_list)})


@frontend.route("/cardlive_search", methods=["POST", "GET"])
def card_live_search():
    client = DBHandler(current_app.config['DB_HOSTNAME'])
    if request.method == "POST":
        if request.form:
            search_word = request.form["query"]
            LOGGER.info(search_word)
            cards = client.get_all_cards_for_ui(value=search_word)
        else:
            cards = client.get_all_cards_for_ui(value="")

    return jsonify({"htmlresponse": render_template("cards_list.html", cards=cards)})


@frontend.route("/export_data", methods=["GET"])
def export_data():
    client = DBHandler(current_app.config['DB_HOSTNAME'])
    filename = client.export_your_collection()
    return send_file(current_app.config['UPLOAD_FOLDER'] + filename, as_attachment=True)


@frontend.route('/uploader', methods=['POST'])
def uploader():
    LOGGER.info(request.files)
    form = UploadForm(request.files)
    LOGGER.info(form)
    LOGGER.info(form.validate())
    LOGGER.info(form.input_file)
    LOGGER.info(form.errors)
    LOGGER.info(form.input_file.errors)
    LOGGER.info(form.submit.errors)
    # TODO : actually import the data lol
    if request.method == 'POST' and form.validate_on_submit():
        input_file = request.files['input_file']
        LOGGER.info(input_file)
        df = pd.read_csv(input_file)
        flash("Your message has been sent. Thank you!", "success")
        LOGGER.info(df)
        error = "SUCESS"
    else:
        LOGGER.info("IN ELSE")
        flash("Your message has been sent. Thank you!", "error")
        error = form.input_file.errors

    flash(error)
    return render_template("options.html", form=UploadForm(), error=error)
