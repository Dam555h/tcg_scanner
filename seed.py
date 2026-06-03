"""
seed.py — populate the database with cards, an admin, and example users.

Run ONCE after setup:
    python seed.py

Card ml_class_name values match the classes from your Teachable Machine project.
"""

from app import create_app, db
from app.models import User, Card, UserCard
import random


# ─── Cards (match your Teachable Machine class labels EXACTLY) ───────────────

CARDS = [
    {
        "name": "Court of Embereth",
        "ml_class_name": "Court Of Embereth",
        "card_type": "Enchantment",
        "rarity": "Rare",
        "description": "At the beginning of your upkeep, you become the monarch's rival. Rewards aggressive, go-wide red decks.",
        "image_url": "",
    },
    {
        "name": "Devilish Valet",
        "ml_class_name": "Devilish Valet",
        "card_type": "Creature — Devil",
        "rarity": "Rare",
        "description": "Whenever another creature enters under your control, Devilish Valet's power doubles until end of turn.",
        "image_url": "",
    },
    {
        "name": "Jetmir, Nexus of Revels",
        "ml_class_name": "Jetmir, Nexus of Revels",
        "card_type": "Legendary Creature — Cat Demon",
        "rarity": "Mythic",
        "description": "Grants escalating bonuses as your board grows: vigilance at 3, trample at 6, double strike at 9 creatures.",
        "image_url": "",
    },
    {
        "name": "Regal Bunnicorn",
        "ml_class_name": "Regal Bunnicorn",
        "card_type": "Creature — Rabbit Unicorn",
        "rarity": "Rare",
        "description": "Power and toughness equal to the number of nonland permanents you control. A one-mana threat that scales fast.",
        "image_url": "",
    },
    {
        "name": "Sol Ring",
        "ml_class_name": "Sol Ring",
        "card_type": "Artifact",
        "rarity": "Uncommon",
        "description": "Tap for two colourless mana. One of the most powerful mana-acceleration artifacts ever printed.",
        "image_url": "",
    },
    {
        "name": "Warren Warleader",
        "ml_class_name": "Warren Warleader",
        "card_type": "Creature — Rabbit Soldier",
        "rarity": "Rare",
        "description": "Creates a 1/1 Rabbit when it attacks, and can grant lifegain or untap your team when creatures deal combat damage.",
        "image_url": "",
    },
]


# ─── Admin + example users ───────────────────────────────────────────────────

ADMIN = {"username": "admin", "password": "admin123", "is_admin": True}

EXAMPLE_USERS = [
    {"username": "sameer", "password": "password123", "is_admin": False},
    {"username": "alice",  "password": "password123", "is_admin": False},
    {"username": "bob",    "password": "password123", "is_admin": False},
    {"username": "charlie","password": "password123", "is_admin": False},
]


def seed():
    app = create_app()
    with app.app_context():
        # Cards
        for data in CARDS:
            if not Card.query.filter_by(ml_class_name=data["ml_class_name"]).first():
                db.session.add(Card(**data))
                print(f"  + card: {data['name']}")
        db.session.commit()

        # Users
        all_user_specs = [ADMIN] + EXAMPLE_USERS
        for spec in all_user_specs:
            if not User.query.filter_by(username=spec["username"]).first():
                u = User(username=spec["username"], is_admin=spec["is_admin"])
                u.set_password(spec["password"])
                db.session.add(u)
                role = "admin" if spec["is_admin"] else "user"
                print(f"  + {role}: {spec['username']}")
        db.session.commit()

        # Give example users some random scanned cards (demo data)
        cards = Card.query.all()
        for spec in EXAMPLE_USERS:
            user = User.query.filter_by(username=spec["username"]).first()
            if user and not UserCard.query.filter_by(user_id=user.id).first():
                for card in random.sample(cards, k=random.randint(2, len(cards))):
                    db.session.add(UserCard(user_id=user.id, card_id=card.id))
        db.session.commit()

        print("\nDone. Login details:")
        print("  ADMIN  -> username: admin    password: admin123")
        print("  USERS  -> sameer / alice / bob / charlie   password: password123")


if __name__ == "__main__":
    seed()
