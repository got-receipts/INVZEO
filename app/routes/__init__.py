from app.routes.auth import auth_bp
from app.routes.admin import admin_bp
from app.routes.cases import cases_bp
from app.routes.departments import departments_bp
from app.routes.main import main_bp
from app.routes.messages import messages_bp
from app.routes.public import public_bp
from app.routes.reports import reports_bp
from app.routes.settings import settings_bp


def register_blueprints(app):
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(cases_bp)
    app.register_blueprint(departments_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(public_bp)
    app.register_blueprint(messages_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(admin_bp)