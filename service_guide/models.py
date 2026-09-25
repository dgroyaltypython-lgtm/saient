from django.db import models


class GeminiConfig(models.Model):
    name = models.CharField(
        max_length=100,
        default="Sai Enterprises Service Guide",
        unique=True,
    )
    api_key = models.TextField(
        blank=True,
        help_text="Gemini API key. This is managed only from Django Admin.",
    )
    model = models.CharField(
        max_length=100,
        default="gemini-3.8-flash",
        help_text="Gemini model ID, for example gemini-3.8-flash.",
    )
    enabled = models.BooleanField(default=True)
    use_google_search = models.BooleanField(
        default=True,
        help_text="Use Gemini Google Search grounding for current service information.",
    )
    system_instruction = models.TextField(
        blank=True,
        help_text="Optional extra instructions for the guide.",
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Gemini Service Guide Settings"
        verbose_name_plural = "Gemini Service Guide Settings"

    def __str__(self):
        return self.name
