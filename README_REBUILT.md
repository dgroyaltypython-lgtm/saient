# Sai Enterprises Office Accounts — Clean Rebuild

This ZIP is a clean rebuild of the Django office accounts project.

## Included

- Sai Enterprises branding
- Login/logout
- StaffProfile office assignment
- Strict staff office isolation
- Global admin access for superusers only
- Multiple active offices
- Daily collection and expense entries
- Cash and UPI
- Search, date and type filters
- Collection, cash, UPI, expense and net totals
- Add, edit and delete entries
- Delete confirmation
- PDF daily report
- WhatsApp daily summary
- Responsive dark/glass UI
- Django admin
- SQLite-compatible migrations
- Stable DailyEntry indexes

## Important database rule

`db.sqlite3` is deliberately NOT included in this rebuild.

If you already have a working database, back it up and keep it. Do not delete it.

## Fresh installation

```powershell
python -m venv saienv
.\saienv\Scripts\activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open:

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/login/`
- `http://127.0.0.1:8000/admin/`

## Existing database

Copy the existing `db.sqlite3` into the project root.

Then:

```powershell
python manage.py showmigrations accounts
python manage.py migrate
python manage.py check
```

Do not run `flush`, do not delete the database, and do not delete existing migration history.

## Staff setup

1. Create a normal Django user.
2. Do NOT enable Django `Staff status` for an ordinary office employee.
3. In Admin, create one `StaffProfile`.
4. Assign exactly one active office.
5. The employee logs in through `/login/`.

A normal staff user cannot select or access another office by changing a URL.

## Admin

Only a Django superuser is treated as a global administrator by the application. A normal employee must not be given Django `Staff status`; their StaffProfile determines their single office.

## Branding

The application is branded **Sai Enterprises** throughout the web UI, PDF report and WhatsApp report.


### Gemini quota/error handling
The Service Guide now keeps Gemini prompts compact, limits output length, handles transient 429/503 errors with a capped retry, and shows a user-friendly quota message instead of exposing the raw API error. Daily/project quota exhaustion is not repeatedly retried.
