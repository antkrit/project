"""
Run application with waitress or gunicorn.
Available on http://host:port.
WARNING: don't use this file in production
"""
import os
from sys import platform
from flask import Flask
from app import app

this_files_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(this_files_dir)

if __name__ == '__main__':
    if platform == 'win32':
        from waitress import serve
        serve(app, host='127.0.0.1', port=8001)  # http://127.0.0.1:8001
    elif platform != 'win32':
        import multiprocessing
        from gunicorn.app.base import BaseApplication

        def number_of_workers():
            """Calculate number of workers"""
            return (multiprocessing.cpu_count() * 2) + 1

        class StandaloneApplication(BaseApplication):
            """
            Application to deploy with gunicorn

            Parameters:
            app (Flask): Flask application
            options (dict): additional arguments

            :param flask_app: Flask application
            :type flask_app: Flask
            :param options: additional arguments, defaults to None
            :type options: dict, optional
            """

            def __init__(self, flask_app, options=None):
                self.options = options or {}
                self.application = flask_app
                super().__init__()

            def load_config(self) -> None:
                """Set options"""
                config = {key: value for key, value in self.options.items()
                          if key in self.cfg.settings and value is not None}
                for key, value in config.items():
                    self.cfg.set(key.lower(), value)

            def load(self) -> "Flask":
                """Returns flask application"""
                return self.application

        custom_options = {
            'bind': '%s:%s' % ('127.0.0.1', '8080'),
            'workers': number_of_workers(),
        }
        StandaloneApplication(app, custom_options).run()  # http://127.0.0.1:8080
