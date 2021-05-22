"""Main script that creates and runs application"""
from module import App
from module.server.view.login import bp as login_bp
from module.server.view.cabinet import bp as cabinet_bp
from module.server.view.admin import bp as admin_bp
from module.commands.common import populate_cli

runner = App()
runner.register_blueprints(login_bp, cabinet_bp, admin_bp)
runner.register_cli_commands(populate_cli)

# Flask app. Required for migration
app = runner.get_flask_app()

if __name__ == "__main__":
    runner.run(__name__)
