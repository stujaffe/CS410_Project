import pandas as pd

from subreddit import Subreddit
from stock_sentiment import StockSentiment

# Register a reddit app at https://www.reddit.com/prefs/apps to get client_id and client_secret
CLIENT_ID = '****'
CLIENT_SECRET = '****'

# Get a single datagram that has titles and comments from rising Reddit posts on 3 popular investment subreddits
def get_trending_subreddits():
    subreddit1 = Subreddit("wallstreetbets", CLIENT_ID, CLIENT_SECRET)
    subreddit2 = Subreddit("investing", CLIENT_ID, CLIENT_SECRET)
    subreddit3 = Subreddit("stocks", CLIENT_ID, CLIENT_SECRET)
    subreddit4 = Subreddit("pennystocks", CLIENT_ID, CLIENT_SECRET)

    subreddit1.initialize()
    subreddit2.initialize()
    subreddit3.initialize()
    subreddit4.initialize()

    df1 = subreddit1.get_all_comments()
    df2 = subreddit2.get_all_comments()
    df3 = subreddit3.get_all_comments()
    df4 = subreddit3.get_all_comments()
    frames = [df1, df2, df3, df4]

    return pd.concat(frames)

# Perform NER and sentiment analysis on Reddit posts datagram
def main():
    df = get_trending_subreddits()
    df.to_csv("posts.csv", encoding='utf-8', index=False)
    df = pd.read_csv("posts.csv")

    stock_sentiment = StockSentiment(df)
    df = stock_sentiment.get_stock_sentiment()
    print(df)


if __name__ == "__main__":
    main()
