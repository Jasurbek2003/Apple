from django.utils.translation import gettext_lazy as _
from django.conf import settings

def get_available_languages():
    """
    Get a list of available languages for the site
    """
    return settings.LANGUAGES

def get_language_name(language_code):
    """
    Get the display name of a language from its code
    """
    for code, name in settings.LANGUAGES:
        if code == language_code:
            return name
    return None