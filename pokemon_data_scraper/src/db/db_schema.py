
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