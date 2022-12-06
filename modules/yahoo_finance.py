import pandas as pd
import logging
import requests
from yahooquery import Ticker
from datetime import datetime
from bs4 import BeautifulSoup
from lxml import etree
from requests.adapters import HTTPAdapter
import urllib3

YAHOO_BASE_URL = "https://finance.yahoo.com/quote/"


def get_historical_data(
    ticker: str,
    start: datetime,
    end: datetime,
    interval: str = "1d",
    type: str = "equity",
) -> pd.DataFrame:
    data_types = ["equity", "options"]
    ticker_data = Ticker(ticker)
    target_data = None

    if type.lower() == "equity":
        target_data = ticker_data.history(start=start, end=end, interval=interval)
    elif type.lower() == "options":
        target_data = ticker_data.option_chain
    else:
        logging.warning(
            f"You entered {type} for the historical data type. Please enter one of: {data_types}."
        )

    return target_data


def __http_adapter(self) -> HTTPAdapter:
    retry_params = urllib3.Retry(
        total=3,
        read=3,
        connect=3,
        backoff_factor=0.5,
        status_forcelist=(400, 404, 500, 502, 504),
        allowed_methods=frozenset(
            ["POST", "HEAD", "TRACE", "GET", "PUT", "OPTIONS", "DELETE"]
        ),
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry_params)
    http = requests.Session()
    http.mount("https://", adapter)
    http.mount("http://", adapter)

    return http


def get_company_name(ticker: str) -> str:
    http = __http_adapter()
    company_name = None
    target_url = YAHOO_BASE_URL + ticker
    try:
        response = http.get(target_url, timeout=2)
    except requests.exceptions.RequestException as e:
        logging.warning(
            f"Received the exception '{e}' while trying to acquire company name for ticker '{ticker}. Please try again."
        )
        return company_name

    contents = response.text
    soup = BeautifulSoup(contents, "lxml")
    dom = etree.HTML(str(soup))

    dom_xpath = dom.xpath("//head//title")
    # target text will be something like: 'General Electric Company (GE) Stock Price, News, Quote & History - Yahoo Finance'
    target_text = dom_xpath[0].text
    # find the location of the ticket symbol and subtract two for the left parenthesis and the space
    loc = target_text.find(ticker.upper()) - 2
    company_name = target_text[:loc]

    return company_name


if __name__ == "__main__":
    pass
