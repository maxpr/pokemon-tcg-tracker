from datetime import datetime, timedelta

import pytz
from clickhouse_driver import Client
import pandas as pd

from pokemon_data_scraper.src.db.db_schema import Extensions, CardList, Collection, Prices
from pokemon_data_scraper.src.logger.logging import LOGGER


class DBHandler:

    def __init__(self, domain: str):
        self.client = Client(domain)

    def list_already_present_extensions(self):
        """Return the extensions code already present in the database.

        :rtype: List
        :return: List of String EXTENSION_CODE. 
        """
        return [val[0] for val in self.client.execute(f"SELECT DISTINCT {Extensions.EXTENSION_CODE} FROM {Extensions}")]

    def get_all_extensions_url_and_code(self, reprocess_all: bool = False):
        """Return the extensions code already present in the database.

        :rtype: List
        :return: List of Extensions.
        """
        if reprocess_all:
            return self.client.execute(f"SELECT {Extensions.EXTENSION_URL}, {Extensions.EXTENSION_CODE} FROM {Extensions}")
        else:
            return self.client.execute(
                f"SELECT {Extensions.EXTENSION_URL}, {Extensions.EXTENSION_CODE} FROM {Extensions} WHERE "
                f"{Extensions.EXTENSION_CODE} NOT IN (SELECT DISTINCT {CardList.CARD_EXTENSION_CODE} FROM {CardList})")

    def insert_extensions(self, dataframe: pd.DataFrame):
        """Insert into the database extensions that don't already exists.

        :param dataframe: Dataframe to insert containing extensions
        """
        # Declare 2 filters. Only take extensions not in DB, and that have released for more than 1 week.
        already_present = self.list_already_present_extensions()
        latest_release_date = datetime.now(tz=pytz.timezone('Asia/Singapore')) - timedelta(days=7)

        # Insert if code is not in DB already, and extensions is released for at least 7 days or more.
        filtered_df = dataframe[(~dataframe[Extensions.EXTENSION_CODE].isin(already_present)) & (
                dataframe[Extensions.EXTENSION_RELEASE_DATE] < latest_release_date)]
        self.client.execute(f"INSERT INTO {Extensions} VALUES", filtered_df.to_dict("records"), types_check=True)

    def insert_cards(self, dataframe: pd.DataFrame):
        """Insert into the database cards.


        :param dataframe: Dataframe to insert containing cards.
        """
        self.client.execute(f"INSERT INTO {CardList} VALUES", dataframe.to_dict("records"), types_check=True)
        self.client.execute(f"OPTIMIZE TABLE {CardList} FINAL DEDUPLICATE")

    def insert_owned_card(self, json_value):
        # Escaping single quote
        escaped_name = json_value[Collection.CARD_NAME].replace("'", "''")
        if len(self.client.execute(f"SELECT {Collection.OWNED} FROM {Collection} "
                                   f"WHERE {Collection.CARD_NAME}='{escaped_name}' AND"
                                   f" {Collection.CARD_EXTENSION_CODE}='{json_value[Collection.CARD_EXTENSION_CODE]}' AND"
                                   f" {Collection.CARD_NUMBER} = {json_value[Collection.CARD_NUMBER]}")) > 0:
            LOGGER.error("UPDATE with name")
            LOGGER.debug(json_value[Collection.CARD_NAME])
            self.client.execute(f"ALTER TABLE {Collection} UPDATE {Collection.OWNED}={int(json_value[Collection.OWNED])} "
                                    f"WHERE {Collection.CARD_NAME}='{escaped_name}' AND"
                                    f" {Collection.CARD_EXTENSION_CODE}='{json_value[Collection.CARD_EXTENSION_CODE]}' AND"
                                    f" {Collection.CARD_NUMBER} = {json_value[Collection.CARD_NUMBER]}")
        else:
            LOGGER.debug("NEW")
            LOGGER.debug(json_value[Collection.CARD_NAME])
            self.client.execute(f"INSERT INTO {Collection} VALUES", [json_value], types_check=True)

    def get_oldest_extension(self):
        """Return the extensions code already present in the database.

        :rtype: datetime
        :return: date of oldest extension.
        """
        return \
        [val[0] for val in self.client.execute(f"SELECT MAX({Extensions.EXTENSION_RELEASE_DATE}) FROM {Extensions}")][0]

    def get_all_extensions_for_ui(self):
        df_ext = self.client.query_dataframe(
            f"SELECT  {Extensions.EXTENSION_NAME}, {Extensions.EXTENSION_CODE},{Extensions.EXTENSION_IMAGE_URL}, {Extensions.EXTENSION_CARD_NUMBER}, {Extensions.EXTENSION_RELEASE_DATE} FROM {Extensions} ORDER BY {Extensions.EXTENSION_RELEASE_DATE} DESCENDING")
        group = self.percent_owned_per_extension()

        df_ext.set_index(Extensions.EXTENSION_CODE, inplace=True)
        df_ext['ownedNumber'] = group
        df_ext['ownedNumber'].fillna(0, inplace=True)
        df_ext.reset_index(inplace=True)
        df_ext['percentage'] = df_ext['ownedNumber'] * 100 / df_ext['extensionCardNumber']
        return df_ext

    def get_card_list_for_extension(self, extension_code: str):
        df = self.client.query_dataframe(
            f"SELECT {CardList.CARD_NAME}, {CardList.CARD_JAPANESE_NAME}, {CardList.CARD_NUMBER}, {CardList.CARD_RARITY}, {CardList.CARD_IMAGE_URL}, {Collection.OWNED}"
            f" FROM {CardList} as cl LEFT JOIN {Collection} as co ON cl.{CardList.CARD_NAME}=co.{Collection.CARD_NAME} AND cl.{CardList.CARD_NUMBER}=co.{Collection.CARD_NUMBER}"
            f" where {CardList.CARD_EXTENSION_CODE} = '{extension_code}' ORDER BY {CardList.CARD_NUMBER} ASCENDING"
        )
        df['cardName'] = df['cardName'].apply(lambda x: x.replace("'", "\\'"))
        return df

    def percent_owned_per_extension(self):
        df = self.client.query_dataframe(f"SELECT {Collection.OWNED},{Collection.CARD_EXTENSION_CODE} FROM {CardList} as cl LEFT JOIN {Collection} as co "
                                         f"ON cl.{CardList.CARD_NAME}=co.{Collection.CARD_NAME} AND"
                                         f" cl.{CardList.CARD_NUMBER}=co.{Collection.CARD_NUMBER} AND"
                                         f" cl.{CardList.CARD_EXTENSION_CODE}=co.{Collection.CARD_EXTENSION_CODE}")

        test = df[df[Collection.OWNED] == 1].groupby(Collection.CARD_EXTENSION_CODE).count()
        group = test[test[Collection.OWNED] != 0]
        return group

    def delete_extension(self, json_value):
        ext_code = json_value[Extensions.EXTENSION_CODE]
        self.client.execute(f"ALTER TABLE {Extensions} DELETE WHERE {Extensions.EXTENSION_CODE} = '{ext_code}'")
        self.client.execute(f"ALTER TABLE {CardList} DELETE WHERE {CardList.CARD_EXTENSION_CODE} = '{ext_code}'")
        self.client.execute(f"ALTER TABLE {Collection} DELETE WHERE {Collection.CARD_EXTENSION_CODE} = '{ext_code}'")
        self.client.execute(f"ALTER TABLE {Prices} DELETE WHERE {Prices.CARD_EXTENSION_CODE} = '{ext_code}'")
