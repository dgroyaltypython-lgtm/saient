from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []

    operations = [
        migrations.CreateModel(
            name="GeminiConfig",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(default="Sai Enterprises Service Guide", max_length=100, unique=True)),
                ("api_key", models.TextField(blank=True, help_text="Gemini API key. This is managed only from Django Admin.")),
                ("model", models.CharField(default="gemini-3.8-flash", help_text="Gemini model ID, for example gemini-3.8-flash.", max_length=100)),
                ("enabled", models.BooleanField(default=True)),
                ("use_google_search", models.BooleanField(default=True, help_text="Use Gemini Google Search grounding for current service information.")),
                ("system_instruction", models.TextField(blank=True, help_text="Optional extra instructions for the guide.")),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Gemini Service Guide Settings",
                "verbose_name_plural": "Gemini Service Guide Settings",
            },
        ),
    ]
