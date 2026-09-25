from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0002_staffprofile"),
    ]

    operations = [
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
    ]
