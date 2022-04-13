from datetime import datetime, timedelta

import pytz
from clickhouse_driver import Client
import pandas as pd

from pokemon_data_scraper.src.db.db_schema import Extensions, CardList


class DBHandler:

    def __init__(self, domain: str):
        self.client = Client(domain)

    def list_already_present_extensions(self):
        """Return the extensions code already present in the database.

        :rtype: List
        :return: List of String EXTENSION_CODE. 
        """
        return [val[0] for val in self.client.execute(f"SELECT DISTINCT {Extensions.EXTENSION_CODE} FROM {Extensions}")]

    def get_all_extensions_url_and_code(self):
        """Return the extensions code already present in the database.

        :rtype: List
        :return: List of Extensions.
        """
        return self.client.execute(f"SELECT {Extensions.EXTENSION_URL}, {Extensions.EXTENSION_CODE} FROM {Extensions}")

    def insert_extensions(self, dataframe: pd.DataFrame):
        """Insert into the database extensions that don't already exists.

        :param dataframe: Dataframe to insert containing extensions
        """
        # Declare 2 filters. Only take extensions not in DB, and that have released for more than 1 week.
        dataframe.to_csv('data.csv')
        already_present = self.list_already_present_extensions()
        latest_release_date = datetime.now(tz=pytz.timezone('Asia/Singapore')) + timedelta(days=7)

        # Insert if code is not in DB already, and extensions is released for at least 7 days or more.
        filtered_df = dataframe[(~dataframe[Extensions.EXTENSION_CODE].isin(already_present)) & (
                    dataframe[Extensions.EXTENSION_RELEASE_DATE] < latest_release_date)]
        self.client.execute(f"INSERT INTO {Extensions} VALUES", filtered_df.to_dict("records"), types_check=True)

    def insert_cards(self,  dataframe: pd.DataFrame):
        """Insert into the database cards.

        :param dataframe: Dataframe to insert containing cards.
        """
        self.client.execute(f"INSERT INTO {CardList} VALUES", dataframe.to_dict("records"), types_check=True)
        self.client.execute(f"OPTIMIZE TABLE {CardList} FINAL DEDUPLICATE")

    def get_oldest_extension(self):
        """Return the extensions code already present in the database.

        :rtype: datetime
        :return: date of oldest extension.
        """
        return [val[0] for val in self.client.execute(f"SELECT MAX({Extensions.EXTENSION_RELEASE_DATE}) FROM {Extensions}")][0]
