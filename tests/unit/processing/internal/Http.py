# -*- coding: utf-8 -*-
from asyncy.processing.internal import Http
from asyncy.processing.internal.Services import Services
from asyncy.utils.HttpUtils import HttpUtils

from pytest import fixture, mark

from tornado.httpclient import AsyncHTTPClient


@fixture
def service_patch(patch):
    patch.object(Services, 'register')


@fixture
def line():
    return {}


@mark.asyncio
async def test_service_http_post(patch, story, line,
                                 service_patch, async_mock):
    patch.object(HttpUtils, 'fetch_with_retry', new=async_mock())
    patch.object(AsyncHTTPClient, '__init__', return_value=None)
    resolved_args = {
        'url': 'https://asyncy.com',
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': '{"foo":"bar"}'
    }

    client_kwargs = {
        'method': 'POST',
        'headers': resolved_args['headers'],
        'body': '{"foo":"bar"}'
    }
    result = await Http.http_post(story, line, resolved_args)
    HttpUtils.fetch_with_retry.mock.assert_called_with(
        1, story.logger, resolved_args['url'],
        AsyncHTTPClient(), client_kwargs
    )
    assert result == HttpUtils.fetch_with_retry.mock().body


@mark.asyncio
async def test_service_http_get(patch, story, line, service_patch, async_mock):
    patch.object(HttpUtils, 'fetch_with_retry', new=async_mock())
    patch.object(AsyncHTTPClient, '__init__', return_value=None)
    resolved_args = {
        'url': 'https://asyncy.com',
        'headers': {
            'X-API-Client': 'engine'
        }
    }

    client_kwargs = {'method': 'GET', 'headers': resolved_args['headers']}
    result = await Http.http_get(story, line, resolved_args)
    HttpUtils.fetch_with_retry.mock.assert_called_with(
        1, story.logger, resolved_args['url'],
        AsyncHTTPClient(), client_kwargs
    )
    assert result == HttpUtils.fetch_with_retry.mock().body


def test_service_http_init():
    Http.init()
