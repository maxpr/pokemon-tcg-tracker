set -e

clickhouse client -n <<-EOSQL
    CREATE DATABASE IF NOT EXISTS pokemon;
    CREATE TABLE IF NOT EXISTS pokemon.extensions(
        extensionName String,
        serie String,
        extensionCode String,
        extensionUrl String,
        extensionImageUrl String,
        extensionReleaseData DateTime('Asia/Singapore')
    ) ENGINE = ReplacingMergeTree()
    ORDER BY (extensionName, serie);

    CREATE TABLE IF NOT EXISTS pokemon.cardList(
        cardName String,
        cardExtensionCode String,
        cardNumber UInt8,
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