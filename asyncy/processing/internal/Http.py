# -*- coding: utf-8 -*-
import certifi

from tornado.httpclient import AsyncHTTPClient

from .Decorators import Decorators
from ...Exceptions import AsyncyError
from ...utils.HttpUtils import HttpUtils


@Decorators.create_service(name='http', command='fetch', arguments={
    'url': {'type': 'string'},
    'headers': {'type': 'map'},
    'body': {'type': 'string'},
    'method': {'type': 'string'}
}, output_type='any')
async def http_post(story, line, resolved_args):
    method = resolved_args.get('method', 'get') or 'get'
    http_client = AsyncHTTPClient()
    kwargs = {'method': method.upper(), 'ca_certs': certifi.where()}
    if resolved_args.get('headers'):
        kwargs['headers'] = resolved_args.get('headers')

    if resolved_args.get('body'):
        kwargs['body'] = resolved_args['body']

    response = await HttpUtils.fetch_with_retry(1, story.logger,
                                                resolved_args['url'],
                                                http_client, kwargs)
    if round(response.code / 100) != 2:
        raise AsyncyError(
            story=story, line=line,
            message=f'Failed to make HTTP call: {response.error}')

    return response.body.decode('utf-8')


def init():
    pass
