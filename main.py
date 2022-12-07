from modules.sentiment import EmbeddedSentiment
from modules.googlenews import GoogleNews
from modules import yahoo_finance as yfin
from modules.utils import logger as lg

import os

DATA_PATH = "./assets/stock_sentiment_data.csv"

if __name__ == "__main__":

    stream_handler = lg.StreamLogging()
    logger = lg.CustomLogger(
        logger_name=os.path.basename(__file__), handlers=[stream_handler]
    ).get_logger()

    gn = GoogleNews()
    ticker = "GOOG"

    company = yfin.get_company_name(ticker=ticker)

    logger.info(f"Searching Google News RSS feed for the ticker '{ticker}'...")
    news_response = gn.search(query=ticker)

    news_df = gn.parse_search_response(response=news_response)
    logger.info(f"Finished searching Google News RSS feed for the ticker '{ticker}'.")

    embed = EmbeddedSentiment()

    logger.info(f"Retrieving stock data embeddings for sentiment analysis.")
    stock_embed_df = embed.get_stock_data_embed(filepath=DATA_PATH, sample=1000)

    print(stock_embed_df)


