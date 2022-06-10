from allianceauth.eveonline.models import EveCharacter
from allianceauth.eveonline.tasks import update_character
from discord import AutocompleteContext, TextChannel, Role, CategoryChannel, option
import pendulum
from .. import app_settings
from django.conf import settings

from allianceauth.services.modules.discord.models import DiscordUser
from django.core.exceptions import ObjectDoesNotExist

from discord.commands import SlashCommandGroup
from discord.ext import commands


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    admin_commands = SlashCommandGroup("admin", "Server Admin Commands", guild_ids=[
                                       int(settings.DISCORD_GUILD_ID)])

    @admin_commands.command(name='add_role', guild_ids=[int(settings.DISCORD_GUILD_ID)])
    async def add_role_slash(self, ctx, channel: TextChannel, role: Role):
        """
        Add a role as read/write to a channel....
        """
        if ctx.author.id not in app_settings.get_admins():  # https://media1.tenor.com/images/1796f0fa0b4b07e51687fad26a2ce735/tenor.gif
            return await ctx.respond(f"You do not have permission to use this command", ephemeral=True)

        await ctx.defer()

        await channel.set_permissions(role, read_messages=True,
                                      send_messages=True)

        await ctx.respond(f"Set Read/Write `{role.name}` in `{channel.name}`")

    @admin_commands.command(name='add_role_read', guild_ids=[int(settings.DISCORD_GUILD_ID)])
    async def add_role_read_slash(self, ctx, channel: TextChannel, role: Role):
        """
        Add a role as read only to a channel....
        """

        # https://media1.tenor.com/images/1796f0fa0b4b07e51687fad26a2ce735/tenor.gif
        if ctx.author.id not in app_settings.get_admins():
            return await ctx.respond(f"You do not have permission to use this command", ephemeral=True)

        await ctx.defer()

        await channel.set_permissions(role, read_messages=True,
                                      send_messages=False)

        await ctx.respond(f"Set Readonly `{role.name}` in `{channel.name}`")

    @admin_commands.command(name='rem_role', guild_ids=[int(settings.DISCORD_GUILD_ID)])
    async def rem_role_slash(self, ctx, channel: TextChannel, role: Role):
        """
        Remove a role from a channel....
        """
        if ctx.author.id not in app_settings.get_admins():  # https://media1.tenor.com/images/1796f0fa0b4b07e51687fad26a2ce735/tenor.gif
            return await ctx.respond(f"You do not have permission to use this command", ephemeral=True)

        await ctx.defer()

        await channel.set_permissions(role, read_messages=False,
                                      send_messages=False)

        await ctx.respond(f"Removed `{role.name}` from `{channel.name}`")

    @admin_commands.command(name='new_channel', guild_ids=[int(settings.DISCORD_GUILD_ID)])
    async def new_channel_slash(self, ctx, category: CategoryChannel, channel_name: str, first_role: Role):
        """
        Create a new channel and add a role....
        """
        if ctx.author.id not in app_settings.get_admins():  # https://media1.tenor.com/images/1796f0fa0b4b07e51687fad26a2ce735/tenor.gif
            return await ctx.respond(f"You do not have permission to use this command", ephemeral=True)

        await ctx.defer()

        found_channel = False

        for channel in ctx.guild.channels:   # TODO replace with channel lookup not loop
            if channel.name.lower() == channel_name.lower():
                found_channel = True

        if not found_channel:
            channel = await ctx.guild.create_text_channel(channel_name.lower(),
                                                          category=category)  # make channel
            await channel.set_permissions(ctx.guild.default_role, read_messages=False,
                                          send_messages=False)

            await channel.set_permissions(first_role, read_messages=True,
                                          send_messages=True)

            await ctx.respond(f"Created New Channel `{channel.name}` and added the `{first_role.name}` Role")

    @admin_commands.command(name='promote_to_god', guild_ids=[int(settings.DISCORD_GUILD_ID)])
    async def promote_role_to_god(self, ctx, role: Role):
        """
        set role as admin....
        """
        if ctx.author.id not in app_settings.get_admins():  # https://media1.tenor.com/images/1796f0fa0b4b07e51687fad26a2ce735/tenor.gif
            return await ctx.respond(f"You do not have permission to use this command", ephemeral=True)

        await ctx.defer(ephemeral=True)

        perms = role.permissions
        perms.administrator = True
        await role.edit(permissions=perms)
        await ctx.respond(f"Set `{role.name}` as admin", ephemeral=True)

    @admin_commands.command(name='demote_from_god', guild_ids=[int(settings.DISCORD_GUILD_ID)])
    async def demote_role_from_god(self, ctx, role: Role):
        """
        revoke role admin....
        """
        if ctx.author.id not in app_settings.get_admins():  # https://media1.tenor.com/images/1796f0fa0b4b07e51687fad26a2ce735/tenor.gif
            return await ctx.respond(f"You do not have permission to use this command", ephemeral=True)

        await ctx.defer(ephemeral=True)

        perms = role.permissions
        perms.administrator = False
        await role.edit(permissions=perms)
        await ctx.respond(f"Removed admin from `{role.name}`", ephemeral=True)

    @admin_commands.command(name='empty_roles', guild_ids=[int(settings.DISCORD_GUILD_ID)])
    async def empty_roles(self, ctx):
        """
        dump all roles with no members.
        """
        if ctx.author.id not in app_settings.get_admins():  # https://media1.tenor.com/images/1796f0fa0b4b07e51687fad26a2ce735/tenor.gif
            return await ctx.respond(f"You do not have permission to use this command", ephemeral=True)

        await ctx.defer()

        empties = []
        for role_model in ctx.guild.roles:
            if len(role_model.members) == 0:
                empties.append(role_model.name)

        await ctx.respond("\n".join(empties))

    @admin_commands.command(name='clear_empty_roles', guild_ids=[int(settings.DISCORD_GUILD_ID)])
    async def clear_empty_roles(self, ctx):
        """
        delete all roles with no members.
        """
        if ctx.author.id not in app_settings.get_admins():  # https://media1.tenor.com/images/1796f0fa0b4b07e51687fad26a2ce735/tenor.gif
            return await ctx.respond(f"You do not have permission to use this command", ephemeral=True)

        await ctx.defer()

        empties = 0
        fails = []
        for role_model in ctx.guild.roles:
            if len(role_model.members) == 0:
                try:
                    await role_model.delete()
                    empties += 1
                except Exception as e:
                    fails.append(role_model.name)

        await ctx.respond(f"Deleted {empties} Roles.")
        chunks = [fails[x:x+50] for x in range(0, len(fails), 50)]
        for c in chunks:
            await ctx.respond("\n".join(c))

    @admin_commands.command(name='orphans', guild_ids=[int(settings.DISCORD_GUILD_ID)])
    async def orphans_slash(self, ctx):
        """
        Returns a list of users on this server, who are not known to AA
        """
        if ctx.author.id not in app_settings.get_admins():  # https://media1.tenor.com/images/1796f0fa0b4b07e51687fad26a2ce735/tenor.gif
            return await ctx.respond(f"You do not have permission to use this command", ephemeral=True)

        await ctx.defer()

        payload = "The following Users cannot be located in Alliance Auth \n"

        member_list = ctx.guild.members
        for member in member_list:
            id = member.id
            try:
                discord_exists = DiscordUser.objects.get(uid=id)
                discord_is_bot = member.bot
            except Exception as e:
                discord_exists = False
                discord_is_bot = False

            try:
                discord_is_bot = member.bot
            except Exception as e:
                discord_is_bot = False

            if discord_exists is not False:
                # nothing to do, the user exists. Move on with ur life dude.
                pass

            elif discord_is_bot is True:
                # lets also ignore bots here
                pass
            else:
                payload = payload + member.mention + "\n"

        try:
            await ctx.respond(payload)
        except Exception as e:
            await ctx.respond(payload[0:1999])

    @admin_commands.command(name='get_webhooks', guild_ids=[int(settings.DISCORD_GUILD_ID)])
    async def get_webhooks(self, ctx):
        """
        Returns the webhooks for the channel
        """
        if ctx.author.id not in app_settings.get_admins():  # https://media1.tenor.com/images/1796f0fa0b4b07e51687fad26a2ce735/tenor.gif
            return await ctx.respond(f"You do not have permission to use this command", ephemeral=True)

        await ctx.defer(ephemeral=True)

        hooks = await ctx.channel.webhooks()
        if len(hooks) == 0:
            name = "{}_webhook".format(ctx.channel.name.replace(" ", "_"))
            hook = await ctx.channel.create_webhook(
                name=name
            )
            await ctx.respond("{} - {}".format(
                hook.name,
                hook.url
            ), ephemeral=True)

        else:
            strs = []
            for hook in hooks:
                strs.append("{} - {}".format(
                    hook.name,
                    hook.url
                ))

            await ctx.respond("\n".join(strs), ephemeral=True)

    @admin_commands.command(name='uptime', guild_ids=[int(settings.DISCORD_GUILD_ID)])
    async def uptime(self, ctx):
        """
        Returns the uptime of the bot
        """
        if ctx.author.id not in app_settings.get_admins():  # https://media1.tenor.com/images/1796f0fa0b4b07e51687fad26a2ce735/tenor.gif
            return await ctx.respond(f"You do not have permission to use this command", ephemeral=True)
        try:
            await ctx.respond(
                pendulum.now(tz="UTC").diff_for_humans(
                    self.bot.currentuptime, absolute=True
                ), ephemeral=True
            )
        except AttributeError:
            await ctx.respond("Still Booting up!", ephemeral=True)

    async def search_characters(ctx: AutocompleteContext):
        """Returns a list of colors that begin with the characters entered so far."""
        return list(EveCharacter.objects.filter(character_name__icontains=ctx.value).values_list('character_name', flat=True)[:10])

    @admin_commands.command(name='force_sync', guild_ids=[int(settings.DISCORD_GUILD_ID)])
    @option("character", description="Search for a Character!", autocomplete=search_characters)
    async def slash_sync(
        self,
        ctx,
        character: str
    ):
        """
        Queue Update tasks for the character and all alts.
        """
        if ctx.author.id not in app_settings.get_admins():
            return await ctx.respond(f"You do not have permission to use this command", ephemeral=True)

        try:
            char = EveCharacter.objects.get(character_name=character)
            alts = char.character_ownership.user.character_ownerships.all().select_related(
                'character').values_list('character__character_id', flat=True)
            for c in alts:
                update_character.delay(c)
            return await ctx.respond(f"Sent tasks to update **{character}**'s Alts")
        except EveCharacter.DoesNotExist:
            return await ctx.respond(f"Character **{character}** does not exist in our Auth system")
        except ObjectDoesNotExist:
            return await ctx.respond(f"**{character}** is Unlinked unable to update characters")


def setup(bot):
    bot.add_cog(Admin(bot))
