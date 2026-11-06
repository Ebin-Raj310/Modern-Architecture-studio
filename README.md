# ARCHITEX - Modern Architecture Studio (Django)

## First-time setup
```
python -m venv venv
venv\Scripts\activate          (Windows)   |   source venv/bin/activate   (Mac/Linux)
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```
Open http://127.0.0.1:8000/

## Email setup (so mails really go out)
1. Copy `.env.example` to `.env` (same folder as `manage.py`).
2. Put your Gmail App Password in `EMAIL_HOST_PASSWORD` (Google Account > Security > App passwords).
3. Test: `python manage.py test_email someone@gmail.com` - it prints the exact reason if it fails.

## Logins
* Any email containing `@` + password of 8+ characters = normal visitor login.
* Admin dashboard: `admin@gmail.com` / `admin123456789` (change in `.env`) -> opens `/admin-dashboard/`.
* After pulling new code always run `python manage.py migrate`.
