# -*- coding: utf-8 -*-
from .Http import Http


class Github:

    api_url = 'https://api.github.com'

    def __init__(self, user=None):
        self.user = user

    def url(self, page):
        pages = {
            'repository': 'repos/{}/{}/contents',
            'installations': 'installations/{}/access_tokens'
        }

        if page in pages:
            base = '{}/{}'.format(self.api_url, '{}')
            return base.format(pages[page])

    def make_url(self, page, *args):
        return self.url(page).format(*args)

    def get_contents(self, organization, repository, file, version=None):
        url = self.make_url('repository', organization, repository, file)
        return Http.get(url, transformation='base64', params={'ref': version})