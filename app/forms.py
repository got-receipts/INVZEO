from __future__ import annotations

from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    PasswordField,
    SelectField,
    SelectMultipleField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional

from app.models import Role


ROLE_CHOICES = [(role.value, role.value.title()) for role in Role]
STATUS_CHOICES = [(value, value) for value in ["Open", "Pending", "Review", "Closed"]]
PRIORITY_CHOICES = [(value, value) for value in ["Low", "Medium", "High", "Critical"]]


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember this device")
    submit = SubmitField("Sign in")


class BootstrapAdminForm(FlaskForm):
    full_name = StringField("Full name", validators=[DataRequired(), Length(max=120)])
    username = StringField("Username", validators=[DataRequired(), Length(max=80)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=255)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=12)])
    confirm_password = PasswordField(
        "Confirm password",
        validators=[DataRequired(), EqualTo("password")],
    )
    department_id = SelectField("Department", coerce=int, validators=[Optional()])
    submit = SubmitField("Create administrator")

    def set_department_choices(self, departments):
        self.department_id.choices = [(0, "No department assigned")] + [
            (department.id, f"{department.name} ({department.county})")
            for department in departments
        ]


class UserForm(FlaskForm):
    full_name = StringField("Full name", validators=[DataRequired(), Length(max=120)])
    username = StringField("Username", validators=[DataRequired(), Length(max=80)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=255)])
    role = SelectField("Role", choices=ROLE_CHOICES, validators=[DataRequired()])
    password = PasswordField("Temporary password", validators=[DataRequired(), Length(min=12)])
    department_id = SelectField("Department", coerce=int, validators=[Optional()])
    submit = SubmitField("Create user")

    def set_department_choices(self, departments):
        self.department_id.choices = [(0, "No department assigned")] + [
            (department.id, f"{department.name} ({department.county})")
            for department in departments
        ]


class DepartmentForm(FlaskForm):
    name = StringField("Department name", validators=[DataRequired(), Length(max=160)])
    county = StringField("County", validators=[DataRequired(), Length(max=80)])
    address = StringField("Address", validators=[DataRequired(), Length(max=255)])
    phone = StringField("Phone", validators=[DataRequired(), Length(max=40)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=255)])
    agency_contact = StringField("Agency contact", validators=[DataRequired(), Length(max=160)])
    notes = TextAreaField("Notes", validators=[Optional(), Length(max=3000)])
    submit = SubmitField("Save department")


class CaseForm(FlaskForm):
    user_name = StringField("User name", validators=[DataRequired(), Length(max=120)])
    primary_department_id = SelectField("Department involved", coerce=int, validators=[DataRequired()])
    department_ids = SelectMultipleField("Attached departments", coerce=int, validators=[Optional()])
    officer_contact = StringField("Officer or agency contact", validators=[DataRequired(), Length(max=160)])
    case_type = StringField("Case type", validators=[DataRequired(), Length(max=120)])
    incident_location = StringField("Incident location", validators=[DataRequired(), Length(max=255)])
    narrative = TextAreaField("Narrative", validators=[DataRequired(), Length(min=20, max=12000)])
    status = SelectField("Status", choices=STATUS_CHOICES, validators=[DataRequired()])
    priority = SelectField("Priority", choices=PRIORITY_CHOICES, validators=[DataRequired()])
    submit = SubmitField("Open case")

    def set_department_choices(self, departments):
        choices = [
            (department.id, f"{department.name} ({department.county})")
            for department in departments
        ]
        self.primary_department_id.choices = choices
        self.department_ids.choices = choices


class CaseNoteForm(FlaskForm):
    body = TextAreaField("Notes", validators=[DataRequired(), Length(min=2, max=4000)])
    submit = SubmitField("Add note")


class ReportForm(FlaskForm):
    title = StringField("Report title", validators=[DataRequired(), Length(max=160)])
    summary = TextAreaField("Executive summary", validators=[Optional(), Length(max=5000)])
    submit = SubmitField("Generate report")


class MessageForm(FlaskForm):
    recipient_id = SelectField("Recipient", coerce=int, validators=[DataRequired()])
    subject = StringField("Subject", validators=[DataRequired(), Length(max=160)])
    body = TextAreaField("Message", validators=[DataRequired(), Length(min=5, max=5000)])
    submit = SubmitField("Send message")

    def set_recipient_choices(self, users):
        self.recipient_id.choices = [
            (user.id, f"{user.full_name} ({user.role.title()})")
            for user in users
        ]


class SettingsForm(FlaskForm):
    full_name = StringField("Full name", validators=[DataRequired(), Length(max=120)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=255)])
    current_password = PasswordField("Current password", validators=[Optional()])
    new_password = PasswordField("New password", validators=[Optional(), Length(min=12)])
    confirm_password = PasswordField(
        "Confirm new password",
        validators=[Optional(), EqualTo("new_password")],
    )
    submit = SubmitField("Save settings")