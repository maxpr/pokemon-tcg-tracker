from decouple import config

from pokemon_data_scraper.src.db.db_connector import DBHandler
from pokemon_data_scraper.src.db.db_schema import create_db_queries
from pokemon_data_scraper.src.logger.logging import LOGGER
from pokemon_data_scraper.src.scraping import scrap_extensions
from pokemon_data_scraper.src.scraping import scrap_cards

if __name__ == '__main__':
    # db_handler = DBHandler(config('DB_URL'))
    #
    # for query in create_db_queries():
    #     LOGGER.info(query)
    #     db_handler.client.execute(query)


    #scrap_extensions.main()
    scrap_cards.main_card_fetching()