from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from functools import wraps
from app.blueprints.admin import admin_bp
from app.models import User, Card, UserCard
from app import db


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated


# ── Dashboard ──────────────────────────────────────────────

@admin_bp.route("/")
@login_required
@admin_required
def dashboard():
    total_users = User.query.count()
    total_cards = Card.query.count()
    total_scans = UserCard.query.count()
    recent_scans = (
        UserCard.query.order_by(UserCard.scanned_at.desc()).limit(8).all()
    )
    top_cards = (
        db.session.query(Card.name, db.func.count(UserCard.id).label("count"))
        .join(UserCard, Card.id == UserCard.card_id)
        .group_by(Card.id)
        .order_by(db.desc("count"))
        .limit(6)
        .all()
    )
    max_count = max([c.count for c in top_cards], default=1)
    return render_template(
        "dashboard.html",
        total_users=total_users,
        total_cards=total_cards,
        total_scans=total_scans,
        recent_scans=recent_scans,
        top_cards=top_cards,
        max_count=max_count,
    )


# ── Users ──────────────────────────────────────────────────

@admin_bp.route("/users")
@login_required
@admin_required
def users():
    all_users = User.query.order_by(User.created_at.desc()).all()
    # count scans per user
    counts = {
        u.id: UserCard.query.filter_by(user_id=u.id).count() for u in all_users
    }
    return render_template("users.html", users=all_users, counts=counts)


@admin_bp.route("/users/<int:user_id>")
@login_required
@admin_required
def user_detail(user_id):
    user = User.query.get_or_404(user_id)
    scans = (
        UserCard.query.filter_by(user_id=user.id)
        .order_by(UserCard.scanned_at.desc())
        .all()
    )
    return render_template("user_detail.html", user=user, scans=scans)


@admin_bp.route("/users/<int:user_id>/toggle-admin", methods=["POST"])
@login_required
@admin_required
def toggle_admin(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("You cannot change your own admin status.", "error")
    else:
        user.is_admin = not user.is_admin
        db.session.commit()
        verb = "granted admin to" if user.is_admin else "removed admin from"
        flash(f"Successfully {verb} {user.username}.", "success")
    return redirect(url_for("admin.users"))


@admin_bp.route("/users/<int:user_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("You cannot delete yourself.", "error")
        return redirect(url_for("admin.users"))
    UserCard.query.filter_by(user_id=user.id).delete()
    db.session.delete(user)
    db.session.commit()
    flash(f"User '{user.username}' deleted.", "success")
    return redirect(url_for("admin.users"))


# ── Cards ──────────────────────────────────────────────────

@admin_bp.route("/cards")
@login_required
@admin_required
def cards():
    all_cards = Card.query.order_by(Card.name).all()
    return render_template("cards.html", cards=all_cards)


@admin_bp.route("/cards/new", methods=["GET", "POST"])
@login_required
@admin_required
def new_card():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        ml_class_name = request.form.get("ml_class_name", "").strip()
        if not name or not ml_class_name:
            flash("Name and ML class name are required.", "error")
        elif Card.query.filter_by(name=name).first():
            flash("A card with that name already exists.", "error")
        elif Card.query.filter_by(ml_class_name=ml_class_name).first():
            flash("That ML class name is already used.", "error")
        else:
            db.session.add(Card(
                name=name,
                ml_class_name=ml_class_name,
                card_type=request.form.get("card_type", "").strip(),
                description=request.form.get("description", "").strip(),
                rarity=request.form.get("rarity", "").strip(),
                image_url=request.form.get("image_url", "").strip(),
            ))
            db.session.commit()
            flash(f"Card '{name}' added.", "success")
            return redirect(url_for("admin.cards"))
    return render_template("card_form.html", card=None)


@admin_bp.route("/cards/<int:card_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit_card(card_id):
    card = Card.query.get_or_404(card_id)
    if request.method == "POST":
        card.name = request.form.get("name", "").strip()
        card.ml_class_name = request.form.get("ml_class_name", "").strip()
        card.card_type = request.form.get("card_type", "").strip()
        card.description = request.form.get("description", "").strip()
        card.rarity = request.form.get("rarity", "").strip()
        card.image_url = request.form.get("image_url", "").strip()
        if not card.name or not card.ml_class_name:
            flash("Name and ML class name are required.", "error")
        else:
            db.session.commit()
            flash(f"Card '{card.name}' updated.", "success")
            return redirect(url_for("admin.cards"))
    return render_template("card_form.html", card=card)


@admin_bp.route("/cards/<int:card_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_card(card_id):
    card = Card.query.get_or_404(card_id)
    UserCard.query.filter_by(card_id=card.id).delete()
    db.session.delete(card)
    db.session.commit()
    flash(f"Card '{card.name}' deleted.", "success")
    return redirect(url_for("admin.cards"))


# ── Scan logs ──────────────────────────────────────────────

@admin_bp.route("/scans")
@login_required
@admin_required
def scans():
    all_scans = (
        UserCard.query.order_by(UserCard.scanned_at.desc()).limit(200).all()
    )
    return render_template("scans.html", scans=all_scans)


@admin_bp.app_errorhandler(403)
def forbidden(e):
    return render_template("403.html"), 403
