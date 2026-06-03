from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    scanned_cards = db.relationship("UserCard", back_populates="user", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"


class Card(db.Model):
    """Master list of all cards the ML model can recognise."""

    __tablename__ = "cards"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    # Must match the Teachable Machine class label EXACTLY
    ml_class_name = db.Column(db.String(120), unique=True, nullable=False)
    card_type = db.Column(db.String(80))
    description = db.Column(db.Text)
    rarity = db.Column(db.String(40))
    image_url = db.Column(db.String(300))

    scanned_by = db.relationship("UserCard", back_populates="card", lazy=True)

    def __repr__(self):
        return f"<Card {self.name}>"


class UserCard(db.Model):
    """Junction table: which users have scanned which cards."""

    __tablename__ = "user_cards"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    card_id = db.Column(db.Integer, db.ForeignKey("cards.id"), nullable=False)
    scanned_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="scanned_cards")
    card = db.relationship("Card", back_populates="scanned_by")

    def __repr__(self):
        return f"<UserCard user={self.user_id} card={self.card_id}>"
