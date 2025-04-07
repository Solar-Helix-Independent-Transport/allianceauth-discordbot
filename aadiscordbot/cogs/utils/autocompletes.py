from discord import AutocompleteContext

from django.db.models import F

from allianceauth.eveonline.models import EveCharacter, EveCorporationInfo


async def search_characters(ctx: AutocompleteContext):
    """Returns a list of Characters Known to auth that begin with the characters entered so far."""
    return [
        a for a in EveCharacter.objects.filter(
            character_name__icontains=ctx.value
        ).values_list(
            'character_name',
            flat=True
        )[:10]
    ]


async def search_mains(ctx: AutocompleteContext):
    """Returns a list of Main Characters that begin with the characters entered so far."""
    return [
        a for a in EveCharacter.objects.filter(
            character_name__icontains=ctx.value,
            character_ownership__user__profile__main_character=F(
                "character_name")
        ).values_list(
            'character_name',
            flat=True
        )[:10]
    ]


async def search_corporations(ctx: AutocompleteContext):
    """Returns a list of Corporations that begin with the characters entered so far."""
    return [
        a for a in EveCorporationInfo.objects.filter(
            corporation_name__icontains=ctx.value
        ).values_list(
            'corporation_name',
            flat=True
        )[:10]
    ]


async def search_corporations_on_characters(ctx: AutocompleteContext):
    """Returns a list of Corporations that begin with the characters entered so far. Sourced from known characters."""
    return list(
        EveCharacter.objects.filter(
            corporation_name__icontains=ctx.value
        ).values_list(
            'corporation_name',
            flat=True
        ).distinct()[:10]
    )
