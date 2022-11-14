from typing import List


class DBInfo:
    """
    Represents the info of the DB
    """

    NAME = "pokemon"


class ExtensionsMeta(type):
    """
    Represents the meta class for this table.

    Basically what it does is change the string representation of the class when the class is directly used as a string.
    (think calling str(extensions) instead of calling str(extensions())).
    """

    def __repr__(self) -> str:
        """Represent name of the class, which is the name of the table."""
        return f"{DBInfo.NAME}.extensions"


class Extensions(metaclass=ExtensionsMeta):
    """This object is a simple enumeration of the name linked to the extensions table."""

    SERIE_NAME = "serieName"
    EXTENSION_NAME = "extensionName"
    EXTENSION_CODE = "extensionCode"
    EXTENSION_URL = "extensionUrl"
    EXTENSION_IMAGE_URL = "extensionImageUrl"
    EXTENSION_RELEASE_DATE = "extensionReleaseDate"
    EXTENSION_CARD_NUMBER = "extensionCardNumber"


class CardListMeta(type):
    """
    Represents the meta class for this table.
    """

    def __repr__(self) -> str:
        """Represent name of the class, which is the name of the table."""
        return f"{DBInfo.NAME}.cardList"


class CardList(metaclass=CardListMeta):
    """This object is a simple enumeration of the name linked to the cardList table."""

    CARD_NAME = "cardName"
    CARD_JAPANESE_NAME = "cardJapaneseName"
    CARD_IMAGE_URL = "cardImageUrl"
    CARD_EXTENSION_CODE = "cardExtensionCode"
    CARD_NUMBER = "cardNumber"
    CARD_RARITY = "cardRarity"


class CollectionMeta(type):
    """
    Represents the meta class for this table.
    """

    def __repr__(self) -> str:
        """Represent name of the class, which is the name of the table."""
        return f"{DBInfo.NAME}.collection"


class Collection(metaclass=CollectionMeta):
    """This object is a simple enumeration of the name linked to the collection table."""

    CARD_NAME = "cardName"
    CARD_NUMBER = "cardNumber"
    CARD_EXTENSION_CODE = "cardExtensionCode"
    OWNED = "owned"


class PricesMeta(type):
    """
    Represents the meta class for this table.
    """

    def __repr__(self) -> str:
        """Represent name of the class, which is the name of the table."""
        return f"{DBInfo.NAME}.prices"


class Prices(metaclass=PricesMeta):
    """This object is a simple enumeration of the name linked to the prices table."""

    CARD_NAME = "cardName"
    CARD_NUMBER = "cardNumber"
    CARD_EXTENSION_CODE = "cardExtensionCode"
    TIMESTAMP_PRICE = "timestampPrice"
    PRICE = "price"


class PriceCollectionTrackingMeta(type):
    """
    Represents the meta class for this table.
    """

    def __repr__(self) -> str:
        """Represent name of the class, which is the name of the table."""
        return f"{DBInfo.NAME}.priceCollectionTracking"


class PriceCollectionTracking(metaclass=PriceCollectionTrackingMeta):
    """This object is a simple enumeration of the name linked to the priceCollectionTracking table."""

    TIMESTAMP_PRICE = "timestampPrice"
    TOTAL_COLLECTION_PRICE = "totalCollectionPrice"


class CollectionTrackingMeta(type):
    """
    Represents the meta class for this table.
    """

    def __repr__(self) -> str:
        """Represent name of the class, which is the name of the table."""
        return f"{DBInfo.NAME}.collectionTracking"


class CollectionTracking(metaclass=CollectionTrackingMeta):
    """This object is a simple enumeration of the name linked to the collectionTracking table."""

    TIMESTAMP_COLLECTION = "timestampCollection"
    EXTENSION_NAME = "extensionName"
    CARD_NUMBER_OWNED = "cardNumberOwned"


def create_db_queries() -> List[str]:
    list_queries = [
        f"CREATE DATABASE IF NOT EXISTS {DBInfo.NAME}",
        f"""CREATE TABLE IF NOT EXISTS {Extensions}(
        {Extensions.SERIE_NAME} String,
        {Extensions.EXTENSION_NAME} String,
        {Extensions.EXTENSION_CODE}  String,
        {Extensions.EXTENSION_URL} String,
        {Extensions.EXTENSION_IMAGE_URL}  String,
        {Extensions.EXTENSION_RELEASE_DATE}  DateTime('Asia/Singapore'),
        {Extensions.EXTENSION_CARD_NUMBER}  UInt16
    ) ENGINE = ReplacingMergeTree()
    ORDER BY ({Extensions.SERIE_NAME} ,{Extensions.EXTENSION_NAME})""",
        f"""CREATE TABLE IF NOT EXISTS {CardList}(
        {CardList.CARD_NAME} String,
        {CardList.CARD_JAPANESE_NAME} String,
        {CardList.CARD_EXTENSION_CODE} String,
        {CardList.CARD_NUMBER} UInt16,
        {CardList.CARD_IMAGE_URL} String,
        {CardList.CARD_RARITY} String
    ) ENGINE = ReplacingMergeTree()
    ORDER BY ({CardList.CARD_NAME}, {CardList.CARD_NUMBER}, {CardList.CARD_EXTENSION_CODE})""",
        f"""CREATE TABLE IF NOT EXISTS {Collection}(
        {Collection.CARD_NAME} String,
        {Collection.CARD_NAME} String,
        {Collection.CARD_NUMBER} UInt8,
        {Collection.CARD_EXTENSION_CODE} String,
        {Collection.OWNED} UInt8
    ) ENGINE = ReplacingMergeTree()
    ORDER BY ({Collection.CARD_NAME}, {Collection.CARD_NUMBER}, {Collection.CARD_EXTENSION_CODE})""",
        f"""CREATE TABLE IF NOT EXISTS {Prices}(
        {Prices.CARD_NAME} String,
        {Prices.CARD_NUMBER} UInt8,
        {Prices.CARD_EXTENSION_CODE} String,
        {Prices.TIMESTAMP_PRICE} DateTime('Asia/Singapore'),
        {Prices.PRICE} Float64
    ) ENGINE = ReplacingMergeTree()
    ORDER BY ({Prices.CARD_NAME}, {Prices.CARD_NUMBER}, {Prices.CARD_EXTENSION_CODE}, {Prices.TIMESTAMP_PRICE})""",
        f"""CREATE TABLE IF NOT EXISTS {PriceCollectionTracking}(
        {PriceCollectionTracking.TIMESTAMP_PRICE} DateTime('Asia/Singapore'),
        {PriceCollectionTracking.TOTAL_COLLECTION_PRICE} Float64
    ) ENGINE = ReplacingMergeTree()
    ORDER BY ({PriceCollectionTracking.TIMESTAMP_PRICE})""",
        f"""CREATE TABLE IF NOT EXISTS {CollectionTracking}(
        {CollectionTracking.TIMESTAMP_COLLECTION} DateTime('Asia/Singapore'),
        {CollectionTracking.EXTENSION_NAME} String,
        {CollectionTracking.CARD_NUMBER_OWNED} UInt8
    ) ENGINE = ReplacingMergeTree()
    ORDER BY ({CollectionTracking.TIMESTAMP_COLLECTION})""",
    ]
    return list_queries
