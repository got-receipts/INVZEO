from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.forms import MessageForm
from app.models import Message, User


messages_bp = Blueprint("messages", __name__, url_prefix="/messages")


@messages_bp.get("")
@login_required
def inbox():
    messages = Message.query.filter_by(recipient_id=current_user.id).order_by(Message.created_at.desc()).all()
    return render_template("messages/list.html", messages=messages)


@messages_bp.route("/compose", methods=["GET", "POST"])
@login_required
def compose():
    form = MessageForm()
    recipients = User.query.filter(User.id != current_user.id).order_by(User.full_name.asc()).all()
    form.set_recipient_choices(recipients)

    if form.validate_on_submit():
        message = Message(
            sender=current_user,
            recipient_id=form.recipient_id.data,
            subject=form.subject.data,
            body=form.body.data,
        )
        db.session.add(message)
        db.session.commit()
        flash("Message sent.", "success")
        return redirect(url_for("messages.inbox"))

    return render_template("messages/compose.html", form=form)


@messages_bp.get("/<int:message_id>")
@login_required
def detail(message_id: int):
    message = Message.query.get_or_404(message_id)
    if message.recipient_id != current_user.id and message.sender_id != current_user.id:
        return render_template("errors/403.html"), 403
    if message.recipient_id == current_user.id and not message.is_read:
        message.is_read = True
        db.session.commit()
    return render_template("messages/detail.html", message=message)