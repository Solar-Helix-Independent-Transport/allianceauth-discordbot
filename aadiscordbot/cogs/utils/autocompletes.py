from discord import AutocompleteContext

from allianceauth.eveonline.models import EveCharacter


async def search_characters(ctx: AutocompleteContext):
    """Returns a list of colors that begin with the characters entered so far."""
    return [
        a async for a in EveCharacter.objects.filter(
            character_name__icontains=ctx.value
        ).values_list(
            'character_name',
            flat=True
        )[:10]
    ]
