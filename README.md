# TCG Scanner

A Flask web app that scans Magic: The Gathering cards with a Teachable Machine
model and saves them to a personal library. Includes a full admin dashboard.

## Features
- Secure login / registration (Flask-Login, hashed passwords)
- Mobile-first camera capture + file upload fallback
- In-browser ML prediction (TensorFlow.js / Teachable Machine)
- Personal card library with collection stats
- Admin dashboard: manage users, manage cards, view scan logs and stats

## Local setup
```bash
pip install -r requirements.txt

# Add your Teachable Machine model (export → TensorFlow.js → download)
# Put model.json, metadata.json, weights.bin in:
#   app/static/my_model/

python seed.py     # creates cards, admin, and example users
python run.py      # visit http://localhost:5000
```

## Test accounts (created by seed.py)
| Role  | Username | Password     |
|-------|----------|--------------|
| Admin | admin    | admin123     |
| User  | sameer   | password123  |
| User  | alice    | password123  |
| User  | bob      | password123  |
| User  | charlie  | password123  |

## Trained ML classes
Court Of Embereth · Devilish Valet · Jetmir, Nexus of Revels ·
Regal Bunnicorn · Sol Ring · Warren Warleader · Nothing (background)

> The `ml_class_name` in the database must match these labels EXACTLY.

## Database (SQLite)
- **users** — id, username, password_hash, is_admin, created_at
- **cards** — id, name, ml_class_name, card_type, description, rarity, image_url
- **user_cards** — id, user_id (FK), card_id (FK), scanned_at

## PythonAnywhere deployment
1. Upload and unzip the project (Files tab → `unzip tcg_scanner.zip`)
2. Bash console: `pip3.10 install --user -r tcg_scanner/requirements.txt`
3. `cd tcg_scanner && python3.10 seed.py`
4. Web tab → Add new web app → Manual config → Python 3.10
5. Source code: `/home/USERNAME/tcg_scanner`
6. Edit the WSGI file:
   ```python
   import sys
   sys.path.insert(0, '/home/USERNAME/tcg_scanner')
   from run import app as application
   ```
7. Upload your model files into `app/static/my_model/`
8. Reload. HTTPS is automatic (required for camera access).

