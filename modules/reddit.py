import requests
import os
from requests.auth import HTTPBasicAuth
import time


class Reddit(object):
    def __init__(
        self, client_id: str, secret_token: str, username: str, password: str
    ) -> None:
        self.client_id = client_id
        self.secret_token = secret_token
        self.username = username
        self.password = password
        self.headers = {}
        self.auth_token_expires = 0
        self.base_url = "https://oauth.reddit.com"

    def _update_auth_token(self, auth_response: dict) -> None:
        auth_token = auth_response.get("access_token")

        try:
            expires_in = auth_response.get("expires_in", 0)
        except TypeError:
            expires_in = 0

        # Auth token expires in current UNIX timestamp plus expiry seconds.
        self.auth_token_expires = int(time.time()) + expires_in
        # Update auth token
        self.auth_token = auth_token

        return None

    def _update_oauth_headers(self) -> dict:

        # Update headers if auth token is less than 5 minutes from expiring (for some wiggle room)
        if self.auth_token_expires <= int(time.time()) + 60 * 5:
            auth = HTTPBasicAuth(username=self.client_id, password=self.secret_token)
            payload = {
                "grant_type": "password",
                "username": self.username,
                "password": self.password,
            }
            headers = {"User-Agent": "CS410_Project/0.0.1"}
            auth_response = requests.post(
                "https://www.reddit.com/api/v1/access_token",
                auth=auth,
                data=payload,
                headers=headers,
            )
            self._update_auth_token(auth_response=auth_response.json())
            auth_token = auth_response.json().get("access_token")
            headers = {**headers, **{"Authorization": f"bearer {auth_token}"}}
            self.headers = headers

    def search_subreddit(self, endpoint: str, search_term: str) -> dict:
        # Always make sure the auth token is up to date
        self._update_oauth_headers()

        params = {"q": search_term}
        response = requests.get(
            self.base_url + str(endpoint), headers=self.headers, params=params
        )

        return response


if __name__ == "__main__":
    pass
