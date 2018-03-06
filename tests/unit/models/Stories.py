# -*- coding: utf-8 -*-
import time

from asyncy.models import BaseModel, Repositories, Stories

from peewee import CharField, ForeignKeyField

from pytest import fixture, mark

from storyscript.parser import Parser
from storyscript.resolver import Resolver


@fixture
def story(repository):
    return Stories(filename='my.story', repository=repository)


def test_stories():
    assert Stories.version.null
    assert isinstance(Stories.filename, CharField)
    assert isinstance(Stories.version, CharField)
    assert isinstance(Stories.repository, ForeignKeyField)
    assert issubclass(Stories, BaseModel)


def test_stories_init(story):
    assert story.parents == []


def test_stories_backend(patch, logger, story):
    patch.object(Repositories, 'backend')
    story.backend(logger, 'app_id', 'pem_path', 'install_id')
    args = (logger, 'app_id', 'pem_path', 'install_id')
    Repositories.backend.assert_called_with(*args)


def test_stories_get_contents(patch, story):
    patch.object(Repositories, 'contents')
    result = story.get_contents()
    Repositories.contents.assert_called_with(story.filename, story.version)
    assert result == Repositories.contents()


def test_stories_data(story):
    story.set_data({})
    assert story.data == {}


def test_stories_environment(patch, story):
    patch.object(Repositories, 'config')
    result = story.environment()
    Repositories.config.assert_called_with('my.story')
    assert result == Repositories.config()


def test_stories_build_tree(patch, story):
    patch.object(Parser, '__init__', return_value=None)
    patch.object(Parser, 'parse')
    patch.object(Stories, 'get_contents')
    story.build_tree()
    Stories.get_contents.assert_called_with()
    assert story.tree == Parser.parse().json()


def test_stories_line(story):
    story.tree = {'script': {'1': 'line one'}}
    assert story.line('1') == story.tree['script']['1']


def test_stories_resolve(patch, magic, logger, story):
    patch.object(Resolver, 'resolve')
    patch.object(Stories, 'line', return_value={'args': {}})
    story.data = {}
    result = story.resolve(logger, '1')
    Stories.line.assert_called_with('1')
    Resolver.resolve.assert_called_with(Stories.line()['args'], {})
    logger.log.assert_called_with('story-resolve', {}, Resolver.resolve())
    assert result == Resolver.resolve()


def test_stories_add_parent(story):
    story.add_parent('parent')
    assert story.parents == ['parent']


def test_stories_add_parent_none(story):
    story.add_parent(None)
    assert story.parents == []


def test_stories_build(patch, logger, application, story):
    patch.object(Stories, 'set_data')
    patch.object(Stories, 'backend')
    patch.object(Stories, 'build_tree')
    patch.object(Stories, 'add_parent')
    story.build(logger, application, '123', 'path')
    Stories.set_data.assert_called_with(application.initial_data)
    Stories.backend.assert_called_with(logger, '123', 'path',
                                       application.installation_id())
    Stories.build_tree.assert_called_with()
    Stories.add_parent.assert_called_with(None)


def test_stories_build_parent(patch, logger, application, story):
    patch.object(Stories, 'set_data')
    patch.object(Stories, 'backend')
    patch.object(Stories, 'build_tree')
    patch.object(Stories, 'add_parent')
    story.build(logger, application, '123', 'path', parent='parent')
    Stories.add_parent.assert_called_with('parent')


def test_stories_start_line(patch, story):
    patch.object(time, 'time', return_value=0)
    story.start_line('1')
    assert story.results['1'] == {'start': time.time()}


def test_stories_end_line(patch, story):
    patch.object(time, 'time', return_value=0)
    story.results = {'1': {'start': 'start'}}
    story.end_line('1', 'output')
    dictionary = {'start': 'start', 'output': 'output', 'end': time.time()}
    assert story.results['1'] == dictionary