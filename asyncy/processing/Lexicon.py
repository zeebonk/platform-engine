# -*- coding: utf-8 -*-
from celery import current_app

import dateparser

from ..Containers import Containers


class Lexicon:
    """
    Lexicon of possible line actions and their implementation
    """

    @staticmethod
    def run(logger, story, line):
        """
        Runs a container with the resolution values as commands
        """
        command = story.resolve(line['args'])
        output = Containers.run(logger, story, line['container'], command)
        story.end_line(line['ln'], output=output)

    @staticmethod
    def set(logger, story, line):
        value = story.resolve(line['args'][1])
        story.environment[line['args'][0]['paths'][0]] = value
        story.end_line(line['ln'])
        return story.next_line(line['ln'])['ln']

    @staticmethod
    def if_condition(logger, story, line):
        """
        Evaluates the resolution value to decide wheter to enter
        inside an if-block.
        """
        result = story.resolve(line['args'])
        if result[0]:
            return line['enter']
        return line['exit']

    @staticmethod
    def unless_condition(logger, story, line):
        result = story.resolve(line['args'])
        if result[0]:
            return line['exit']
        return line['enter']

    @staticmethod
    def next(logger, story, line):
        result = story.resolve(line['args'])
        if result.endswith('.story'):
            return result
        return '{}.story'.format(result)

    @staticmethod
    def wait(logger, story, line):
        logger.log('lexicon-wait', line)
        waiting_time = story.resolve(line['args'])
        eta = dateparser.parse('in {}'.format(waiting_time))
        kwargs = {'block': line['ln'], 'environment': story.environment}
        current_app.send_task('asyncy.CeleryTasks.process_story',
                              args=[story.app_id, story.name], kwargs=kwargs,
                              eta=eta)
        next_line = story.next_line(line['exit'])
        story.end_line(line['ln'])
        if next_line:
            return next_line['ln']
