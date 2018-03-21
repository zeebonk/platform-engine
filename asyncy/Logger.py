# -*- coding: utf-8 -*-
from logging import LoggerAdapter

from frustum import Frustum

from logdna import LogDNAHandler


class Adapter(LoggerAdapter):

    def process(self, message, kwargs):
        app = self.extra['app']
        story = self.extra['story']
        result = '{}::{} {}'.format(app, story, message)
        return result, kwargs


class Logger:

    events = [
        ('container-start', 'info', 'Container {} is running'),
        ('container-end', 'info', 'Container {} has finished'),
        ('story-start', 'info',
         'Start processing story "{}" for app {} with id {}'),
        ('story-save', 'info', 'Saved results of story "{}" for app {}'),
        ('story-end', 'info',
         'Finished processing story "{}" for app {} with id {}'),
        ('task-received', 'info', 'Received task for app {} with story "{}"'),
        ('container-volume', 'debug', 'Created volume {}'),
        ('lexicon-wait', 'debug', 'Processing line {} with "wait" method'),
        ('story-execution', 'debug', 'Received line "{}" from handler'),
        ('story-resolve', 'debug', 'Resolved "{}" to "{}"')
    ]

    def __init__(self, config):
        self.frustum = Frustum(config.logger_name, config.logger_level)
        self.logdna_key = config.logdna_key

    def logdna_handler(self, key, options):
        return LogDNAHandler(key, options)

    def add_logdna(self):
        options = {}
        handler = self.logdna_handler(self.logdna_key, options)
        self.frustum.logger.addHandler(handler)

    def adapter(self, app, story):
        return Adapter(self.frustum.logger, {'app': app, 'story': story})

    def start(self):
        for event in self.events:
            self.frustum.register_event(event[0], event[1], event[2])
        self.frustum.start_logger()
        self.add_logdna()

    def log(self, event, *args):
        self.frustum.log(event, *args)
