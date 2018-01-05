# -*- coding: utf-8 -*-
from evenflow.Github import Github
from evenflow.Http import Http
from evenflow.models import Users

from pytest import fixture, mark


@fixture
def user():
    return Users('name', 'email', '@handle')


@fixture
def gh(user):
    return Github(user=user)


def test_github(user, gh):
    assert gh.api_url == 'https://api.github.com'
    assert gh.user is user


def test_github_no_user():
    github = Github()
    assert github.user is None


@mark.parametrize('page, url', [
    ('repository', 'repos/{}/{}/contents'),
    ('installations', 'installations/{}/access_tokens')
])
def test_github_url_repository(gh, page, url):
    expected = '{}{}'.format('https://api.github.com/', url)
    assert gh.url(page) == expected


def test_github_url_none(gh):
    assert gh.url('magic') is None


def test_github_make_url(mocker, gh):
    mocker.patch.object(Github, 'url', return_value='test/{}')
    result = gh.make_url('page', 'argument')
    Github.url.assert_called_with('page')
    assert result == 'test/argument'


def test_get_contents(mocker, gh):
    mocker.patch.object(Http, 'get')
    mocker.patch.object(Github, 'make_url')
    result = gh.get_contents('org', 'repo', 'file')
    Github.make_url.assert_called_with('repository', 'org', 'repo', 'file')
    Http.get.assert_called_with(Github.make_url(), transformation='base64',
                                params={'ref': None})
    assert result == Http.get()


def test_get_contents_version(mocker, gh):
    mocker.patch.object(Http, 'get')
    mocker.patch.object(Github, 'make_url')
    gh.get_contents('org', 'repo', 'file', 'version')
    Http.get.assert_called_with(Github.make_url(), transformation='base64',
                                params={'ref': 'version'})