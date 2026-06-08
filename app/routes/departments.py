from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import login_required

from app.extensions import db
from app.forms import DepartmentForm
from app.models import Department, Role
from app.services.security import roles_required


departments_bp = Blueprint("departments", __name__, url_prefix="/departments")


@departments_bp.get("")
@login_required
def list_departments():
    departments = Department.query.order_by(Department.county.asc(), Department.name.asc()).all()
    return render_template("departments/list.html", departments=departments)


@departments_bp.route("/new", methods=["GET", "POST"])
@roles_required(Role.ADMIN.value, Role.OFFICER.value, Role.ANALYST.value)
def new_department():
    form = DepartmentForm()
    if form.validate_on_submit():
        department = Department(
            name=form.name.data,
            county=form.county.data,
            address=form.address.data,
            phone=form.phone.data,
            email=form.email.data.lower(),
            agency_contact=form.agency_contact.data,
            notes=form.notes.data,
        )
        db.session.add(department)
        db.session.commit()
        flash("Department added.", "success")
        return redirect(url_for("departments.list_departments"))

    return render_template("departments/new.html", form=form)