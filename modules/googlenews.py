"""
Class to scrape GoogleNews. Much credit goes to: https://github.com/kotartemiy/pygooglenews
The PyPI package from the link above was not used since it had older dependencies that were not compatible with newer versions of Python.
"""

from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from dateparser import parse as parse_date
from lxml import etree
from fake_useragent import UserAgent
import pandas as pd
import requests
from requests.adapters import HTTPAdapter
import urllib3
from urllib3.exceptions import ReadTimeoutError, ResponseError, MaxRetryError
from typing import List


class GoogleNews(object):
    def __init__(self, lang="en", country="US", timeout=3):
        self.lang = lang.lower()
        self.country = country.upper()
        self.BASE_URL = "https://news.google.com/rss"
        self.timeout = timeout

    def _ceid(self):
        """Compile correct country-lang parameters for Google News RSS URL"""
        return "?ceid={}:{}&hl={}&gl={}".format(
            self.country, self.lang, self.lang, self.country
        )

    def _from_to_helper(self, validate=None):
        try:
            validate = parse_date(validate).strftime("%Y-%m-%d")
            return str(validate)
        except:
            raise Exception("Could not parse your date")

    def _create_headers(self):
        headers = {"User-Agent": UserAgent().random}
        return headers

    def _http_adapter(self) -> HTTPAdapter:
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

    def search(self, query: str, helper=True, when=None, from_date=None, to_date=None):

        if when:
            query += " when:" + when

        if not when and from_date:
            from_date = self._from_to_helper(validate=from_date)
            query += " after:" + from_date

        if not when and to_date:
            from_date = self._from_to_helper(validate=to_date)
            query += " before:" + to_date

        if helper == True:
            query = quote_plus(query)

        search_ceid = self._ceid()
        search_ceid = search_ceid.replace("?", "&")

        http = self._http_adapter()
        response = http.get(
            self.BASE_URL + "/search?q={}".format(query) + search_ceid,
            headers=self._create_headers(),
            timeout=self.timeout,
        )

        return response

    def get_canonical_url(self, rss_url: str, retries: int = 0, max_retries=3) -> str:
        canonical_url = None
        http = self._http_adapter()
        try:
            response = http.get(
                rss_url,
                headers=self._create_headers(),
                timeout=self.timeout,
            )
        except (
            ReadTimeoutError,
            ResponseError,
            MaxRetryError,
            requests.exceptions.ConnectionError,
            requests.exceptions.ConnectTimeout,
        ):
            return canonical_url
        soup = BeautifulSoup(response.text, "lxml")
        dom = etree.HTML(str(soup))
        element = dom.xpath("//head//link[@rel='canonical']")
        try:
            canonical_url = element[0].get("href")
        except IndexError:
            return canonical_url

        if "http" not in canonical_url:
            try:
                element = dom.xpath("//head//link[@rel='alternate']")
                canonical_url = element[0].get("href")
            except IndexError:
                return canonical_url

        return canonical_url

    def get_article_conents(self, canonical_url: str, query_terms: List[str]) -> list:
        content = []
        if canonical_url is None:
            return content
        if type(query_terms) == str:
            query_terms = [query_terms]
        http = self._http_adapter()
        try:
            response = http.get(
                canonical_url,
                headers=self._create_headers(),
                timeout=self.timeout,
            )
        except (
            ReadTimeoutError,
            ResponseError,
            MaxRetryError,
            requests.exceptions.ConnectionError,
            requests.exceptions.ConnectTimeout,
        ):
            return content
        soup = BeautifulSoup(response.text, "lxml")
        # Get all p tags
        all_ps = soup.find_all("p")

        for x in all_ps:
            for q in query_terms:
                if q in str(x):
                    content.append(str(x))
                    # Only need one of the query terms to match
                    break

        return content

    def parse_search_response(self, response: requests.models.Response) -> pd.DataFrame:

        soup = BeautifulSoup(response.text, "xml")

        items = [x for x in soup.find_all("item")]
        dates = [x.find("pubDate").text for x in items]
        dates = [parse_date(x).strftime("%Y-%m-%d") for x in dates]
        titles = [x.find("title").text for x in items]
        links_rss = [x.find("link").text for x in items]
        links_canon = [self.get_canonical_url(x) for x in links_rss]

        for url in links_canon:
            content = self.get_article_conents(canonical_url=url, query_terms=["MSFT"])
            contents.append(content)

        output = pd.DataFrame(
            list(zip(dates, titles, links_rss, links_canon, contents)),
            columns=["date", "title", "link_rss", "links_canonical", "article_content"],
        )

        return output


if __name__ == "__main__":

    gn = GoogleNews()

    response = gn.search(query="MSFT")

    df = gn.parse_search_response(response=response)

    canonicals = df.loc[:, "links_canonical"]

    contents = []
    for url in canonicals:
        content = gn.get_article_conents(canonical_url=url, query_terms=["MSFT"])
        contents.append(content)

    for c in contents:
        print(len(c))
