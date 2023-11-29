"""Helium Solana constants."""
DOMAIN = "helium_solana"

INTEGRATION_GENERAL_STATS = "general_stats"
INTEGRATION_GENERAL_TOKEN_PRICE = "general_token_price"
INTEGRATION_WALLET = "wallet"

CONF_VERSION = "version"
CONF_TITLE = "title"
CONF_WALLETS = "wallets"
CONF_WALLET = "wallet"
CONF_WALLET_COUNT = "wallet_count"
CONF_HOTSPOTS = "hotspots"
CONF_PRICES = "prices"
CONF_INTEGRATION = "integration"
CONF_INTEGRATION_OPTIONS = {
    INTEGRATION_GENERAL_STATS: "General Helium Stats",
    INTEGRATION_GENERAL_TOKEN_PRICE: "Token Prices",
    INTEGRATION_WALLET: "Wallet",
}

HOTSPOTTY_STATS = "https://beta-api.hotspotty.net/api/v1/stats"
HOTSPOTTY_PRICES = "https://beta-api.hotspotty.net/api/v1/tokens/prices"
HOTSPOTTY_HOTSPOT_INFO = "https://beta-api.hotspotty.net/api/v1/wallets/hotspots/"
HOTSPOTTY_REWARDS = "https://beta-api.hotspotty.net/api/v1/hotspot/rewards/lifetime/11AbnisrSShDiscZxxsyKVEpAjFCWtytkpt1atmChBSECBgSrv6/"
HOTSPOTTY_TOKEN = "5b3l5f19oksqw22ssjdh7g3kjsvgh1a2"

JUPITER_PRICE_URL = "https://quote-api.jup.ag/v4/price"  # ?ids=a,b,c,d
COINGECKO_PRICE_URL = "https://api.coingecko.com/api/v3/simple/price"
EPOCH_INFO_URL = "https://hnt-explorer.herokuapp.com/v1/epoch/info"
DELEGATED_STAKES_URL = "https://hnt-explorer.herokuapp.com/v1/delegated_stakes/info"

BACKEND_URL = "http://solana.oerdek.com"
BACKEND_KEY = "JEcbtHfDsWYmIlnOBrtn"

ADDRESS_IOT = "iotEVVZLEywoTn1QdwNPddxPWszn3zFhEot3MfL9fns"
ADDRESS_HNT = "hntyVP6YFm1Hg25TN9WGLqM12b8TQmcknKrdu1oxWux"
ADDRESS_MOBILE = "mb1eu7TzEc71KxDpsmsKoucSSuuoGLv1drys1oP2jh6"
ADDRESS_SOLANA = "So11111111111111111111111111111111111111112"

CURRENCY_USD = "USD"

TOKEN_HELIUM = "HNT"
TOKEN_IOT = "IOT"
TOKEN_MOBILE = "MOBILE"
TOKEN_SOL = "SOL"
