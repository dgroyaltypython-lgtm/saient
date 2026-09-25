from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


@login_required
def dashboard(request):
    """Legacy route: the Service Guide now lives inside the main dashboard."""
    return redirect("dashboard")


@login_required
def clear_chat(request):
    """Legacy route kept so old bookmarks do not break."""
    return redirect("dashboard")
