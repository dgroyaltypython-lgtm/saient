# Office Isolation Fix

This version fixes a critical role-semantics issue.

- `is_global_admin()` is based on `user.is_superuser` only.
- A normal employee with a `StaffProfile` is restricted to that profile's active office.
- Normal employees receive no office queryset/list in the dashboard.
- `get_allowed_office()` rejects a staff user's attempt to access another office ID.
- Add/edit/delete/PDF/WhatsApp all use the same server-side access check.
- Do not set Django `Staff status` on ordinary employees.
- Use a superuser for the global administrator account.

If a user previously had `is_staff=True`, remove Staff status in Django Admin and keep their StaffProfile assigned to exactly one office.
