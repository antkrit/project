"""Adds CLI commands to the manager"""
from flask_script import Manager, Shell
from flask_migrate import MigrateCommand
from module.app import app
from module.commands.common import PytestCommand, make_context_, populate_manager

manager = Manager(app)
manager.add_command('db', MigrateCommand)  # work with migrations
manager.add_command('test', PytestCommand)  # run tests
manager.add_command('shell', Shell(make_context=make_context_))  # runs python shell
manager.add_command("populate", populate_manager)  # fill database with test data

if __name__ == '__main__':
    manager.run()
