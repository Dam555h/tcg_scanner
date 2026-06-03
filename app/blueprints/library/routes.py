from flask import render_template
from flask_login import login_required, current_user
from app.blueprints.library import library_bp
from app.models import UserCard, Card


@library_bp.route("/")
@login_required
def library():
    user_cards = (
        UserCard.query
        .filter_by(user_id=current_user.id)
        .order_by(UserCard.scanned_at.desc())
        .all()
    )
    total_cards = Card.query.count()
    return render_template(
        "library.html",
        user_cards=user_cards,
        total_cards=total_cards,
    )
