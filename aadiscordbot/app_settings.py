from django.conf import settings
import re

def get_site_url():  # regex sso url
    regex = r"^(.+)\/s.+"
    matches = re.finditer(regex, settings.ESI_SSO_CALLBACK_URL, re.MULTILINE)
    url = "http://"

    for m in matches:
        url = m.groups()[0] # first match

    return url

def authanalitics_active():
    return 'authanalitics' in settings.INSTALLED_APPS