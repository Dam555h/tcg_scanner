from flask import render_template, request, jsonify
from flask_login import login_required, current_user
from app.blueprints.scan import scan_bp
from app.models import Card, UserCard
from app import db


# Minimum confidence for a scan to count as a match
CONFIDENCE_THRESHOLD = 0.80


@scan_bp.route("/")
@login_required
def scanner():
    return render_template("scanner.html")


@scan_bp.route("/predict", methods=["POST"])
@login_required
def predict():
    """
    Receives JSON: { "class_name": "...", "confidence": 0.95 }
    The TensorFlow.js / Teachable Machine prediction runs in the browser.
    This route looks up the card and saves it to the user's library.
    """
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "No data received."}), 400

    class_name = data.get("class_name", "").strip()
    confidence = float(data.get("confidence", 0))

    # "Nothing" is the background class - treat as no card detected
    if class_name.lower() == "nothing":
        return jsonify({
            "success": False,
            "message": "No card detected. Point the camera directly at a card.",
        })

    if confidence < CONFIDENCE_THRESHOLD:
        return jsonify({
            "success": False,
            "message": f"Not confident enough ({confidence:.0%}). Try better lighting and hold steady.",
        })

    card = Card.query.filter_by(ml_class_name=class_name).first()
    if not card:
        return jsonify({
            "success": False,
            "message": f"Card '{class_name}' is not in the database yet.",
        })

    already = UserCard.query.filter_by(
        user_id=current_user.id, card_id=card.id
    ).first()

    if not already:
        db.session.add(UserCard(user_id=current_user.id, card_id=card.id))
        db.session.commit()

    return jsonify({
        "success": True,
        "already_owned": bool(already),
        "confidence": round(confidence, 3),
        "card": {
            "name": card.name,
            "card_type": card.card_type,
            "description": card.description,
            "rarity": card.rarity,
            "image_url": card.image_url,
        },
    })
