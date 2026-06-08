from flask import Blueprint, flash, redirect, render_template, url_for

from app.extensions import db
from app.forms import UserForm
from app.models import AuditLog, Department, Role, User
from app.services.security import roles_required


admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("", methods=["GET", "POST"])
@roles_required(Role.ADMIN.value)
def dashboard():
    form = UserForm()
    form.set_department_choices(Department.query.order_by(Department.name.asc()).all())
    if form.validate_on_submit():
        user = User(
            full_name=form.full_name.data,
            username=form.username.data.lower(),
            email=form.email.data.lower(),
            role=form.role.data,
            department_id=form.department_id.data or None,
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("User created.", "success")
        return redirect(url_for("admin.dashboard"))

    users = User.query.order_by(User.created_at.desc()).all()
    audit_logs = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(50).all()
    return render_template("admin/dashboard.html", form=form, users=users, audit_logs=audit_logs)