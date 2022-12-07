import praw
import requests
import pandas as pd


class Subreddit(object):
    """
    Represents top titles and posts of a subreddit
    """

    def __init__(self, subreddit, client_id, client_secret):
        self.posts = []
        self.subreddit = subreddit
        self.reddit = praw.Reddit(
            # Register a reddit app at https://www.reddit.com/prefs/apps to get client_id and client_secret
            client_id=client_id,
            client_secret=client_secret,
            user_agent='CS410 BOT',
        )

    def initialize(self):
        self.get_top_posts()
        self.populate_post_responses()

    # Fetch all the top level posts that are considered "rising" on the target subreddit
    def get_top_posts(self):
        headers = {'User-Agent': 'CS410/1.0.0'}
        url = 'http://reddit.com/r/{0}/rising.json'.format(self.subreddit)

        res = requests.get(url, headers=headers)
        data = res.json()

        post_list = data['data']['children']

        for c in post_list:
            data = c['data']
            targetData = {'title': data['title'], 'id': data['id'], 'responses': []}
            self.posts.append(targetData)

    # Get the responses/comments for all the "rising" posts on the target subreddit
    def populate_post_responses(self):
        for post in self.posts:
            submission = self.reddit.submission(post['id'])
            submission.comments.replace_more(limit=0)

            for top_level_comment in submission.comments:
                post['responses'].append(top_level_comment.body)

            if post['responses']:
                del post['responses'][0]  # remove metadata from responses

    # Flatten post titles and comments into a single Pandas dataframe and return it
    def get_all_comments(self):
        """
        Returns all post text and response text in a list
        """
        all_comments = []
        titles = [o['title'] for o in self.posts]
        all_comments.extend(titles)
        for post in self.posts:
            responses = post['responses']
            all_comments.extend(responses)

        return pd.DataFrame(all_comments, columns=['posts'])


if __name__ == "__main__":
    pass
