
from modules.sentiment import EmbeddedSentiment
from modules.googlenews import GoogleNews
from modules import yahoo_finance as yfin


if __name__ == "__main__":
    gn = GoogleNews()
    ticker = "GOOG"

    company = yfin.get_company_name(ticker=ticker)

    news_response = gn.search(query=ticker)

    news_df = gn.parse_search_response(response=news_response)