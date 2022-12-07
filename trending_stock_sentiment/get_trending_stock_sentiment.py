import pandas as pd

from source.subreddit import Subreddit
from source.stock_sentiment import StockSentiment

# Register a reddit app at https://www.reddit.com/prefs/apps to get client_id and client_secdret
CLIENT_ID = '****'
CLIENT_SECRET = '****'


def get_trending_subreddits():
    subreddit1 = Subreddit("wallstreetbets", CLIENT_ID, CLIENT_SECRET)
    subreddit2 = Subreddit("investing", CLIENT_ID, CLIENT_SECRET)
    subreddit3 = Subreddit("stocks", CLIENT_ID, CLIENT_SECRET)

    subreddit1.initialize()
    subreddit2.initialize()
    subreddit3.initialize()

    df1 = subreddit1.get_all_comments()
    df2 = subreddit2.get_all_comments()
    df3 = subreddit3.get_all_comments()
    frames = [df1, df2, df3]

    return pd.concat(frames)


def main():
    df = get_trending_subreddits()
    df.to_csv("posts.csv", encoding='utf-8', index=False)
    df = pd.read_csv("posts.csv")

    stock_sentiment = StockSentiment(df)
    df = stock_sentiment.get_stock_sentiment()
    print(df)


if __name__ == "__main__":
    main()
