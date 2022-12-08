# Overview
This project provides a suite of tools to retrieve trending news and social media posts along with mechanisms to extract relevant entities from this text to perform sentiment analysis. Consult the sections below for descriptions of the included tools, use cases and instructions for setup and operation.

## Setup / Requirements
- Development and testing was done with Python 3.9
- A Reddit user account is required
- A registered Reddit application is needed to get a client_id and client_secret.[See Reddit App Documentation](https://www.reddit.com/prefs/apps) 
- It's highly recommended to use a Python virtual environment, either via `python3 -m venv venv` or an external tool such as `pyenv` where you can control the Python version within the virtual environment as well.
- Install Python libraries via `pip install -r requirements.txt`
- Install spacy model en_core_web_sm using `python -m spacy download en_core_web_sm`

## Trending Reddit Stock Sentiment
This tool uses Reddit APIs along with Python lib `praw` to fetch all the trending posts and responses in each of the posts from popular stock/investment subreddits (wallstreetbets, stocks, investing by default). 
This text is stored in a Pandas dataframe. NLP is performed on the dataframe using `spacy` using the `en_core_web_sm` model. NER is performed and filtering is performed to 
leave only stock symbols, company names and other potential investment targets. Finally the NLP library `flair` is used to generate a sentiment score for each post. 

The intended purpose of this tool is to allow users to pick up the latest sentiments on popular investment entities based on trending Reddit activity. 


## How To Run
1. Consult `get_trending_stock_sentiment.py` and view the `main` function for an example of how to use this tool.
2. You can run the current implementation from OUTSIDE (in the main project folder) the `trending_stock_sentiment` directory by using the command line: `python3 trending_stock_sentiment/get_trending_stock_sentiment.py`.


### Example Output
Using the public Reddit APIs to fetch rising/trending Reddit posts on popular investment subreddits:
![image info](./img/posts.png)

Using `praw` to fetch reddit comments to the previously retrieved rising posts
![image info](./img/responses.png)

A Pandas DataFrame with Reddit posts, extracted NERs and sentiments after processing with `spacy` and `flair`
![image info](./img/ner_sentiment_df.png)

### Known Issues
NLP is difficult and social media posts contain a great deal of word level and syntactic ambiguity. Often times the predicted sentiment will not actually apply to the extracted entity because the
input text is actually not referring to the detected entity. There are many other ways that ambiguity invalidates the results of our tool. Additionally, the processing of raw social media posts present 
a significant data cleaning problem. This issue also complicates the task of named entity recognition. It is difficult to avoid picking up non-relevant terms as investment entities. 



## Google News Sentiment Plus Stock Returns

### Overview
This functionality will take a stock ticker symbol e.g. `GOOG`, search the Google News RSS feed for that ticker symbol, take each RSS feed URL, scrape the article page via the RSS feed URL for the canonical url (e.g. `www.nytimes.com/articleX`) since the RSS feed URL is not directly scrapable, and then scrape the artcile page via the canonical URL, where possible. Once the web pages are scraped, the program will assign a sentiment scores the to news article titles and the article content.

### How To Run
You can experiment with the Google News sentiment functionality as follows:
1. From the command line run `python3 main_gnews.py [TICKER SYMBOL] [SAMPLE SIZE] [K]`. E.g. `python3 main_gnews.py AAPL 2000 150`. If you do not supply a ticker symbol or supply an invalid ticker symbol, an exception will be raised. If you do not supply a proper float or integer for `SAMPLE SIZE` or `K`, an exception will also be raised.
2. Explaination of inputs:
- TICKER SYMBOL: The stock you wish to investigate.
- SAMPLE SIZE: The number of observations you wish to sample from the data file. The SBERT bi-encoding is much faster than BERT cross-encoding, but choosing a sample size in the tens of thousands will take quite a while.
- K: The number of nearest neighbors the embedded sample size analysis will take into account. `K` should be less than `SAMPLE SIZE`. If it is greater, then the program will default to `K = SAMPLE SIZE`.
4. You should see some logging messages about what's happening. Sometimes the process takes several minutes due to the web scraping and word embedding process.
5. The logging messages should tell that it saved the ticker symbol output files in the folder `output`.

### Sentiment Scoring Methods
## Rule Based
Utilizes the `Vader` senitment scorer. This is a lexicon and rules-based sentiment classifier, which means it has difficulty with words it doesn't already know and has trouble with context. It outputs a dictionary of scores, positive/neutral/negative/compound. The compound score is a wegighted average of sorts and is utilized in the program's rules based senitment scores for news articles.
## Embedded Based
Utilizes the Sentence-BERT (SBERT), a bi-encoder version of the BERT transformer that is much faster at encoding sentences than BERT. The news article titles are embedded with SBERT, then compared to a random sample of labeled sentiment data from stocks that is kept in the `assets` folder. Ideally the entire labeled sentiment data would be used, but it has 100,000+ data points so that is not feasible in the time allotated (it takes around 90 minutes to embed all 100,000+ data points on a CPU machine). In order to decide a sentiment score, the title embedding's K nearest neighbors are taken from the random sample based on cosine similarity. The average of the binary 0/1 sentiment scores is taken as the embedded sentiment score.
A similar process is done for the news article's contents. However, the contents are lists of sentneces so each sentence in one article is embedded and compared with the random sample from the labeled file, then the entire article's contents are averaged for the sentiment score.

### Stock Returns
Yahoo Finance data is utilzed to calculate stock return data (with dividends reinvested). In order to calculate return, the earliest news story date and the latest news story date are taken as the beginning and end of the stock holding period. The average yearly return is calculated based on the holding period, no matter how long the holding period was.

### Output
Returns a summary JSON file and a CSV file via a Pandas DataFrame in the a folder called `output` (the folder will be created if it doesn't already exist).
Exmaple summary output:
```
{
    "ticker": "GOOG",
    "company_name": "Alphabet Inc.",
    "earliest_news_date": "2022-04-20",
    "latest_news_date": "2022-12-08",
    "news_title_sentiment_KNN": 0.5103,
    "news_title_sentiment_rules": 0.10207299999999998,
    "article_sentiment_KNN": 0.5045454545454545,
    "article_sentiment_rules": 0.12450454545454546,
    "stock_market_return": -0.397369190693005
}
```

### Known Issues
It's difficult to create a scraping tool that will be able to scrape all types of different webpages that arise from the Google News RSS feed. Some website are behind a paywall, some use dynamically rendered content via JavaScript, HTML tags change, etc. In addition, while the labeled sentiment data is financial and stock related, a generic transformer model like SBERT is still being used without more fine-tuning to deal with the uniquness of the NLP data here.

## Other Tools

### Reddit Search
There is a module called `reddit.py` in the `modules` folder that allows you to search for Reddit posts. So, you can search for `GOOG` but this time on WallStreetBets. In order to access this part of the Reddit API, you need the `client_id` and `secret_token` mentioned above, but also a Reddit login and password. These variables are outlined in `.env.sample` and can be passed as environmental variables in the `reddit.py` `Reddit` class. A similar logic can be followed as with Google News to analyze the Reddit posts from WallStreetBets or other sub-Reddits.
