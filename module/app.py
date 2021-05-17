"""Main script that creates and runs application"""
from module import App
from module.server.view.login import bp as login_bp
from module.server.view.cabinet import bp as cabinet_bp
from module.server.view.admin import bp as admin_bp

runner = App()
runner.register_blueprints(login_bp, cabinet_bp, admin_bp)

# Flask app. Needed to make a migration
app = runner.get_flask_app()

runner.run(__name__)
