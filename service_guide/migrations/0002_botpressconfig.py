from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("service_guide", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="BotpressConfig",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        default="Sai Enterprises Service Guide",
                        max_length=100,
                        unique=True,
                    ),
                ),
                (
                    "enabled",
                    models.BooleanField(
                        default=True,
                        help_text="Show the Botpress Service Guide inside the main dashboard.",
                    ),
                ),
                (
                    "inject_script_url",
                    models.URLField(
                        default="https://cdn.botpress.cloud/webchat/v3.3/inject.js",
                        help_text="Botpress Webchat loader URL from your Botpress embed code.",
                    ),
                ),
                (
                    "embed_script_url",
                    models.URLField(
                        blank=True,
                        help_text=(
                            "Paste the second <script src=...> URL from Botpress Webchat → "
                            "Deploy Settings → Embed code."
                        ),
                    ),
                ),
                (
                    "element_id",
                    models.CharField(
                        default="bp-embedded-webchat",
                        help_text=(
                            "HTML element ID configured in Botpress Deploy Settings when "
                            "Chat interface is set to Embedded."
                        ),
                        max_length=100,
                    ),
                ),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Botpress Service Guide Settings",
                "verbose_name_plural": "Botpress Service Guide Settings",
            },
        ),
    ]
