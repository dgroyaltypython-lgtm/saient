from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Office",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120)),
                ("address", models.TextField(blank=True)),
                ("phone", models.CharField(blank=True, max_length=30)),
                ("whatsapp", models.CharField(blank=True, max_length=30)),
                ("active", models.BooleanField(default=True)),
            ],
            options={"ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="DailyEntry",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("entry_date", models.DateField()),
                ("entry_type", models.CharField(choices=[("collection", "Collection"), ("expense", "Expense")], max_length=20)),
                ("amount", models.DecimalField(decimal_places=2, max_digits=12)),
                ("payment_mode", models.CharField(choices=[("cash", "Cash"), ("upi", "UPI")], max_length=10)),
                ("reason", models.CharField(max_length=255)),
                ("notes", models.TextField(blank=True)),
                ("reference", models.CharField(blank=True, max_length=100)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("office", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="entries", to="accounts.office")),
            ],
            options={
                "ordering": ["-entry_date", "-created_at"],
                "indexes": [
                    models.Index(fields=["office", "entry_date"], name="accounts_da_office__b3d7c7_idx"),
                    models.Index(fields=["entry_type"], name="accounts_da_entry_t_5f2c4b_idx"),
                ],
            },
        ),
    ]
