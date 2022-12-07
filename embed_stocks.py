
from modules.sentiment import EmbeddedSentiment
import pandas as pd

DATA_PATH = "./assets/stock_sentiment_data.csv"


if __name__ == "__main__":
    
    embed = EmbeddedSentiment()

    stock_df = pd.read_csv(filepath_or_buffer=DATA_PATH, header=0, index_col=0)
    
    sentences = list(stock_df["Sentence"])

    embeddings = embed.create_embeddings(sentences, progress_bar=True)

    stock_df["Embeddings"] = list(embeddings)

    stock_df.to_csv("stock_sentiment_embed.csv")
