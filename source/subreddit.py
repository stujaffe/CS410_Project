import praw
import requests


class Subreddit(object):
    """
    Represents top titles and posts of a subreddit
    """

    def __init__(self, subreddit):
        self.posts = []
        self.subreddit = subreddit
        self.reddit = praw.Reddit(
            # Register a reddit app at https://www.reddit.com/prefs/apps to get client_id and client_secdret
            client_id='ADD_CLIENT_ID',
            client_secret='ADD_SECRET',
            user_agent='CS410 BOT',
        )

    def initialize(self):
        self.get_top_posts()
        self.populate_post_responses()

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

    def populate_post_responses(self):
        for post in self.posts:
            submission = self.reddit.submission(post['id'])
            submission.comments.replace_more(limit=0)

            for top_level_comment in submission.comments:
                post['responses'].append(top_level_comment.body)

            del post['responses'][0]  # remove metadata from responses


def main():
    subreddit = Subreddit("wallstreetbets")
    subreddit.initialize()


if __name__ == '__main__':
    main()
