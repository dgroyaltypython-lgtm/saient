"""Legacy Service Guide admin module.

The Service Guide is now powered by Botpress Webchat embedded in the main
Sai Enterprises dashboard. Gemini is no longer used by the application.
The legacy GeminiConfig model remains in the database only so existing
migrations/data are not destroyed.
"""

from accounts.admin import site

# Intentionally no Gemini admin registration.
# Botpress Webchat configuration is supplied by the published Botpress embed.
