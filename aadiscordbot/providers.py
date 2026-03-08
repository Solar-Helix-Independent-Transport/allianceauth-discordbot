from esi.openapi_clients import ESIClientProvider

from . import __title__, __version__

esi_openapi = ESIClientProvider(
    ua_appname=__title__,
    ua_url="https://github.com/Solar-Helix-Independent-Transport/allianceauth-discordbot",
    ua_version=__version__,
    compatibility_date="2025-12-16",
    operations=[
        "GetSovereigntyStructures",
        "GetUniverseSystemsSystemId",
        "GetUniverseConstellationsConstellationId",
        "GetUniverseRegionsRegionId",
        "GetCharactersCharacterIdSearch",
        "GetAlliancesAllianceId",
        "PostUniverseNames"
    ]
)
