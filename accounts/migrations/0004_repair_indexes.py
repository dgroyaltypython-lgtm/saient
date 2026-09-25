from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0003_merge_20260925_0017"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql=[
                        'CREATE INDEX IF NOT EXISTS "dailyentry_office_date_idx" ON "accounts_dailyentry" ("office_id", "entry_date");',
                        'CREATE INDEX IF NOT EXISTS "dailyentry_type_date_idx" ON "accounts_dailyentry" ("entry_type", "entry_date");',
                    ],
                    reverse_sql=[
                        'DROP INDEX IF EXISTS "dailyentry_office_date_idx";',
                        'DROP INDEX IF EXISTS "dailyentry_type_date_idx";',
                    ],
                ),
            ],
            state_operations=[
                migrations.AddIndex(
                    model_name="dailyentry",
                    index=models.Index(
                        fields=["office", "entry_date"],
                        name="dailyentry_office_date_idx",
                    ),
                ),
                migrations.AddIndex(
                    model_name="dailyentry",
                    index=models.Index(
                        fields=["entry_type", "entry_date"],
                        name="dailyentry_type_date_idx",
                    ),
                ),
            ],
        ),
    ]
