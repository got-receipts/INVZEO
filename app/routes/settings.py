from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.forms import SettingsForm


settings_bp = Blueprint("settings", __name__, url_prefix="/settings")


@settings_bp.route("", methods=["GET", "POST"])
@login_required
def index():
    form = SettingsForm(obj=current_user)
    if form.validate_on_submit():
        current_user.full_name = form.full_name.data
        current_user.email = form.email.data.lower()
        if form.new_password.data:
            if not current_user.check_password(form.current_password.data or ""):
                flash("Current password did not match.", "danger")
                return redirect(url_for("settings.index"))
            current_user.set_password(form.new_password.data)
        db.session.commit()
        flash("Settings updated.", "success")
        return redirect(url_for("settings.index"))
    return render_template("settings/index.html", form=form)