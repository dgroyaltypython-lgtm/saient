import random
import time

from django.core.exceptions import ImproperlyConfigured

from .models import GeminiConfig


DEFAULT_INSTRUCTION = """
You are Sai Enterprises Service Guide, a helpful multilingual guide for people
who need help with online government, education, certificates, applications,
forms and other public services, especially in India and Maharashtra.

Understand and respond naturally in English, Hindi, Marathi, or a mixture of
these languages. Prefer the user's language unless they ask for another one.

Your job is to GUIDE, not to submit applications or make decisions for the user.
Explain processes step by step in simple language. When a form is involved,
explain what each field generally means and what information belongs there.

For current government rules, fees, dates, portals, document requirements or
procedures, use Google Search grounding when available and prefer official
government, university, board or other authoritative sources. Clearly tell the
user when a detail should be verified on the official portal.

Never ask for or repeat passwords, OTPs, UPI PINs, ATM PINs, CVV numbers,
full payment-card details, or other authentication secrets. Do not claim that
you have submitted a form, paid a fee, booked an appointment, or completed a
government service unless the application itself actually provides such an action.

If the user is unsure which service they need, ask one or two short clarifying
questions. Otherwise give a practical numbered checklist.

For important current information, include the official website name or source
link when the API provides grounded sources.
""".strip()


class GeminiQuotaError(RuntimeError):
    """A friendly application-level error for Gemini quota/rate-limit failures."""


def get_config():
    config = GeminiConfig.objects.order_by("id").first()
    if not config:
        return None
    if not config.enabled or not config.api_key.strip():
        return None
    return config


def _is_retryable_api_error(exc):
    text = str(exc).upper()
    return (
        "429" in text
        or "RESOURCE_EXHAUSTED" in text
        or "RATE_LIMIT_EXCEEDED" in text
        or "TOO_MANY_REQUESTS" in text
        or "503" in text
        or "UNAVAILABLE" in text
    )


def _is_quota_exhausted_error(exc):
    text = str(exc).upper()
    # Daily quota / exhausted prepaid credits should not be hammered with retries.
    return (
        "QUOTA_EXCEEDED" in text
        or "GENERATE_REQUESTS_PER_DAY" in text
        or "GENERATE_CONTENT_FREE_TIER_REQUESTS" in text
        or "PREPAY" in text
        or "CREDIT BALANCE" in text
        or "DAILY QUOTA" in text
    )


def _friendly_api_error(exc):
    text = str(exc).lower()

    if "429" in text or "resource_exhausted" in text or "rate_limit" in text:
        if _is_quota_exhausted_error(exc):
            return GeminiQuotaError(
                "Gemini daily/project quota is exhausted. "
                "Please check the Gemini API usage and billing/quota settings, "
                "or try again after the quota resets."
            )
        return GeminiQuotaError(
            "Gemini is temporarily rate-limited. "
            "Please wait a little and try again. If this continues, "
            "check the Gemini API quota and billing settings."
        )

    if "401" in text or "api key" in text and "invalid" in text:
        return RuntimeError(
            "The Gemini API key is invalid or expired. "
            "Please update it in Admin → Gemini Service Guide Settings."
        )

    if "403" in text or "permission_denied" in text:
        return RuntimeError(
            "Gemini rejected the API key or project permission. "
            "Please check the Gemini project and API key in Admin."
        )

    if "404" in text or "model_not_found" in text:
        return RuntimeError(
            "The configured Gemini model was not found. "
            "Please check the model name in Admin → Gemini Service Guide Settings."
        )

    return exc


def ask_gemini(message, history=None):
    config = get_config()
    if not config:
        raise ImproperlyConfigured(
            "Gemini is not configured. A superuser must add the Gemini API key in Admin."
        )

    try:
        from google import genai
        from google.genai import types
    except ImportError as exc:
        raise ImproperlyConfigured(
            "The google-genai package is not installed. Run: pip install -r requirements.txt"
        ) from exc

    client = genai.Client(api_key=config.api_key.strip())

    # Keep the prompt compact so repeated questions consume fewer input tokens.
    # We store more history in the session, but send only the most recent turns.
    parts = []
    for item in (history or [])[-6:]:
        role = "User" if item.get("role") == "user" else "Guide"
        content = (item.get("content") or "").strip()
        if content:
            # Prevent a very long previous answer from becoming the next prompt.
            parts.append(f"{role}: {content[:3500]}")

    parts.append(f"User: {message.strip()[:3500]}")
    prompt = "\n\n".join(parts)

    instruction = DEFAULT_INSTRUCTION
    if config.system_instruction.strip():
        instruction += (
            "\n\nAdditional administrator instructions:\n"
            + config.system_instruction.strip()
        )

    tools = []
    if config.use_google_search:
        tools.append(types.Tool(google_search=types.GoogleSearch()))

    generation_config = types.GenerateContentConfig(
        system_instruction=instruction,
        # A shorter default response reduces token usage while still allowing
        # useful step-by-step service guidance.
        max_output_tokens=1000,
        tools=tools or None,
    )

    model = config.model.strip() or "gemini-3.8-flash"

    # The SDK may already retry transient 429/5xx errors. This small
    # application-level retry is deliberately capped so an exhausted daily
    # quota is not hammered repeatedly.
    last_exc = None
    for attempt in range(2):
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config=generation_config,
            )
            break
        except Exception as exc:
            last_exc = exc
            if not _is_retryable_api_error(exc) or _is_quota_exhausted_error(exc):
                raise _friendly_api_error(exc)
            if attempt == 1:
                raise _friendly_api_error(exc)
            time.sleep(1.0 + random.uniform(0, 0.4))
    else:
        raise _friendly_api_error(last_exc)

    text = (response.text or "").strip()
    if not text:
        raise RuntimeError("Gemini returned an empty response.")

    sources = []
    try:
        metadata = response.candidates[0].grounding_metadata
        for chunk in (metadata.grounding_chunks or []):
            web = getattr(chunk, "web", None)
            uri = getattr(web, "uri", None)
            title = getattr(web, "title", None)
            if uri and uri not in [item["url"] for item in sources]:
                sources.append({"title": title or uri, "url": uri})
    except (AttributeError, IndexError, TypeError):
        pass

    return {"text": text, "sources": sources}
