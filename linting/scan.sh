#/bin/bash
MODULE_NAME="pokemon_data_scraper flask_app"
#
black $MODULE_NAME
isort --atomic .
pylint $MODULE_NAME
mypy --config-file pyproject.toml --install-types $MODULE_NAME