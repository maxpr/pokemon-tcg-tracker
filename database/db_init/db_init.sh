set -e

clickhouse client -n <<-EOSQL
    CREATE DATABASE IF NOT EXISTS pokemon;
    CREATE TABLE IF NOT EXISTS pokemon.extensions(
        serieName String,
        extensionName String,
        extensionCode String,
        extensionUrl String,
        extensionImageUrl String,
        extensionReleaseDate DateTime('Asia/Singapore'),
        extensionCardNumber UInt8
    ) ENGINE = ReplacingMergeTree()
    ORDER BY (serieName ,extensionName);

    CREATE TABLE IF NOT EXISTS pokemon.cardList(
        cardName String,
        cardJapaneseName String,
        cardExtensionCode String,
        cardNumber UInt8,
        cardImageUrl String,
        cardRarity String
    ) ENGINE = ReplacingMergeTree()
    ORDER BY (cardName, cardExtensionCode);

    CREATE TABLE IF NOT EXISTS pokemon.collection(
        cardName String,
        cardExtensionCode String,
        owned UInt8
    ) ENGINE = ReplacingMergeTree()
    ORDER BY (cardName, cardExtensionCode);

    CREATE TABLE IF NOT EXISTS pokemon.prices(
        cardName String,
        cardNameExtensionCode UInt64,
        timestampPrice DateTime('Asia/Singapore'),
        price Float64
    ) ENGINE = ReplacingMergeTree()
    ORDER BY (cardName, cardNameExtensionCode, timestampPrice);

    CREATE TABLE IF NOT EXISTS pokemon.priceCollectionTracking(
        timestampPrice DateTime('Asia/Singapore'),
        totalCollectionPrice Float64
    ) ENGINE = ReplacingMergeTree()
    ORDER BY (timestampPrice);

    CREATE TABLE IF NOT EXISTS pokemon.collectionTracking(
        timestampCollection DateTime('Asia/Singapore'),
        extensionName String,
        cardNumberOwned UInt8
    ) ENGINE = ReplacingMergeTree()
    ORDER BY (timestampCollection);
EOSQL