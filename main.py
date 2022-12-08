from modules.sentiment import EmbeddedSentiment, RuleBasedSentiment
from modules.googlenews import GoogleNews
from modules.yahoo_finance import YahooFinance
from modules.utils import logger as lg

import os
from datetime import datetime
import numpy as np
import json
import pandas as pd

DATA_PATH = "./assets/stock_sentiment_data.csv"
OUTPUT_FOLDER = "./output/"

stream_handler = lg.StreamLogging()
logger = lg.CustomLogger(
    logger_name=os.path.basename(__file__), handlers=[stream_handler]
).get_logger()


def output_to_json(output: dict, output_path: str) -> None:

    output_dir = "/".join(output_path.split("/")[:-1])
    if os.path.exists(output_dir):
        with open(output_path, "w") as f:
            json.dump(obj=output, fp=f, indent=4)
    else:
        os.makedirs(output_dir)
        with open(output_path, "w") as f:
            json.dump(obj=output, fp=f, indent=4)

    return None


def output_to_csv(df: pd.DataFrame, output_path: str) -> None:

    output_dir = "/".join(output_path.split("/")[:-1])
    if os.path.exists(output_dir):
        df.to_csv(path_or_buf=output_path, header=True)
    else:
        os.makedirs(output_dir)
        df.to_csv(path_or_buf=output_path, header=True)

    return None


if __name__ == "__main__":

    gn = GoogleNews()
    yfin = YahooFinance()
    embed = EmbeddedSentiment()
    rules = RuleBasedSentiment()

    ticker = "GOOG"
    company = yfin.get_company_name(ticker=ticker)
    logger.info(f"Searching Google News RSS feed for the ticker '{ticker}'...")
    news_response = gn.search(query=ticker)
    news_df = gn.parse_search_response(response=news_response)
    logger.info(f"Finished searching Google News RSS feed for the ticker '{ticker}'.")
    logger.info(f"Retrieving stock data embeddings for sentiment analysis.")
    stock_embed_df = embed.get_stock_data_embed(filepath=DATA_PATH, sample=1000)
    # Vecotrize the Embeddings properly
    stock_embeddings = np.asarray(stock_embed_df["Embeddings"].tolist())

    # Compare news titles to the stock embeddings
    news_titles = news_df["title"].tolist()
    title_sentiment_embed = []
    title_sentiment_rules = []
    for title in news_titles:
        title_embed = embed.create_embeddings(query=title)
        similarity_scores = embed.calc_dot_product(
            vector1=title_embed, vector2=stock_embeddings
        )
        closest_matches_idx = embed.get_closest_matches(
            similarity_scores=similarity_scores, limit=100
        )
        sentiment = embed.get_sentiment_scores(
            indices=closest_matches_idx, sentiment_labels=stock_embed_df["Sentiment"]
        )
        title_sentiment_embed.append(sentiment)
        title_sentiment_rules.append(rules.get_compound_score(query=title))

    # Add to news dataframe
    news_df["title_sentiment_embed"] = title_sentiment_embed
    news_df["title_sentiment_rules"] = title_sentiment_rules

    # Now compare the article content, if it exists, to the stock embeddings.
    article_content = news_df["article_content"]
    article_content_sentiment_embed = []
    article_content_sentiment_rules = []
    for content in article_content:
        # article_content is a list of lists so we need to go through the sub-list as well
        content_sentiment_embed = []
        content_sentiment_rules = []
        for paragraph in content:
            paragraph_embed = embed.create_embeddings(query=paragraph)
            similarity_scores = embed.calc_dot_product(
                vector1=paragraph_embed, vector2=stock_embeddings
            )
            closest_matches_idx = embed.get_closest_matches(
                similarity_scores=similarity_scores, limit=100
            )
            sentiment_embed = embed.get_sentiment_scores(
                indices=closest_matches_idx,
                sentiment_labels=stock_embed_df["Sentiment"],
            )
            content_sentiment_embed.append(sentiment_embed)
            content_sentiment_rules.append(rules.get_compound_score(query=paragraph))
        # Calculate average for the content (i.e. row in the news_df), if it exists
        if len(content_sentiment_embed) > 0:
            mean_content_sentiment_embed = sum(content_sentiment_embed) / len(
                content_sentiment_embed
            )
        else:
            # Pick an obvious score if it's empty
            mean_content_sentiment_embed = -999
        if len(content_sentiment_rules) > 0:
            mean_content_sentiment_rules = sum(content_sentiment_rules) / len(
                content_sentiment_rules
            )
        else:
            # Pick an obvious score if it's empty
            mean_content_sentiment_rules = -999

        article_content_sentiment_embed.append(mean_content_sentiment_embed)
        article_content_sentiment_rules.append(mean_content_sentiment_rules)

    # Add to news dataframe
    news_df["article_sentiment_embed"] = article_content_sentiment_embed
    news_df["article_sentiment_rules"] = article_content_sentiment_rules

    yearly_return = yfin.calculate_return(
        ticker=ticker,
        start=datetime.strptime(min(news_df["date"]), "%Y-%m-%d"),
        end=datetime.strptime(max(news_df["date"]), "%Y-%m-%d"),
    )

    output_dict = {
        "ticker": ticker,
        "company_name": company,
        "earliest_news_date": min(news_df["date"]),
        "latest_news_date": max(news_df["date"]),
        "news_title_sentiment_KNN": float(
            news_df[news_df["title_sentiment_embed"] > -999][
                "title_sentiment_embed"
            ].mean()
        ),
        "news_title_sentiment_rules": float(
            news_df[news_df["title_sentiment_rules"] > -999][
                "title_sentiment_rules"
            ].mean()
        ),
        "article_sentiment_KNN": float(
            news_df[news_df["article_sentiment_embed"] > -999][
                "title_sentiment_embed"
            ].mean()
        ),
        "article_sentiment_rules": float(
            news_df[news_df["article_sentiment_rules"] > -999][
                "title_sentiment_rules"
            ].mean()
        ),
        "stock_market_return": float(yearly_return),
    }

    output_to_json(
        output_dict, output_path=OUTPUT_FOLDER + f"{ticker}_google_news_summary.json"
    )
    output_to_csv(news_df, output_path=OUTPUT_FOLDER + f"{ticker}_google_news_data.csv")
