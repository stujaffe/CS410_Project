import pandas as pd
import logging
import requests
import numpy as np
from yahooquery import Ticker
from datetime import datetime
from bs4 import BeautifulSoup
from lxml import etree
from requests.adapters import HTTPAdapter
import urllib3


class YahooFinance(object):
    def __init__(self, base_url="https://finance.yahoo.com/quote/"):
        self.base_url = base_url

    @staticmethod
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
        # Add row index
        target_data["index"] = target_data.reset_index().index
        target_data.reset_index(inplace=True)
        target_data.set_index("index", inplace=True)

        return target_data

    def calculate_return(self, ticker: str, start: datetime, end: datetime) -> float:
        """
        Assumes shares are bought on the open price of the start date and sold at the close on the end date.
        Dividends are reinvested at the next day's opening price.
        Splits are already accounted for in Yahoo Finance data.
        """
        # Store the following data in a list of tuples: (buy date, price, shares)
        dividend_list = []
        shares = 1
        data = self.get_historical_data(ticker=ticker, start=start, end=end)
        buy_price = data["open"][0]
        sell_price = data["close"][data.shape[0] - 1]
        # Reinvest dividends
        try:
            dividend_idx = data.index[data["dividends"] > 0].tolist()
        except KeyError:
            dividend_idx = []
        # Calculate extra shares
        for idx in dividend_idx:
            # Handle if the dividend was paid on the last row of the datafame
            try:
                div_shares = data.loc[idx, "dividends"] / data.loc[idx + 1, "open"]
                div_date = data.loc[idx + 1, "date"]
                share_price = data.loc[idx + 1, "open"]
                dividend_list.append((div_date, share_price, div_shares))
            except KeyError:
                # Add back in to closing price otherwise
                div_amount = data.loc[idx, "dividends"]
                sell_price += div_amount
        # Calculate total dollars received at sale
        for div in dividend_list:
            shares += div[2]
        proceeds = shares * sell_price

        # Calculate time weighted yearly return
        # First get the weighted share years since we don't want to count holding the partial dividend shares as high as whole shares.
        total_days = (end - start).days
        # The single share of stock has the full days
        share_days = total_days * 1
        for div in dividend_list:
            # Holding period of partial stock from dividend reinvestment times the number of shares
            div_days = (
                end - datetime(div[0].year, div[0].month, div[0].day)
            ).days * div[2]
            share_days += div_days

        # Yearly average return
        yearly_ret = (proceeds / buy_price) ** (1 / (share_days / 365.0)) - 1

        return yearly_ret

    @staticmethod
    def __http_adapter() -> HTTPAdapter:
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

    def get_company_name(self, ticker: str) -> str:
        http = self.__http_adapter()
        company_name = None
        target_url = self.base_url + ticker
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
