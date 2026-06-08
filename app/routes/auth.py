from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.extensions import db
from app.forms import BootstrapAdminForm, LoginForm
from app.models import Department, Role, User
from app.services.security import log_audit

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if User.query.count() == 0:
        return redirect(url_for("auth.bootstrap_admin"))
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            log_audit("login", user=user, details="User signed in")
            return redirect(url_for("main.dashboard"))
        flash("Invalid email or password.", "danger")

    return render_template("auth/login.html", form=form)


@auth_bp.route("/bootstrap", methods=["GET", "POST"])
def bootstrap_admin():
    if User.query.count() > 0:
        return redirect(url_for("auth.login"))

    form = BootstrapAdminForm()
    form.set_department_choices(Department.query.order_by(Department.name.asc()).all())
    if form.validate_on_submit():
        admin = User(
            full_name=form.full_name.data,
            username=form.username.data.lower(),
            email=form.email.data.lower(),
            role=Role.ADMIN.value,
            department_id=form.department_id.data or None,
        )
        admin.set_password(form.password.data)
        db.session.add(admin)
        db.session.commit()
        login_user(admin)
        log_audit("bootstrap_admin", user=admin, details="Initial administrator account created")
        flash("Administrator account created.", "success")
        return redirect(url_for("main.dashboard"))

    return render_template("auth/bootstrap.html", form=form)


@auth_bp.get("/logout")
@login_required
def logout():
    log_audit("logout", user=current_user, details="User signed out")
    logout_user()
    return redirect(url_for("auth.login"))