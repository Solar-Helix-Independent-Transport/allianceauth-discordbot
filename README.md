# AA-Discordbot

AA-Discordbot for [Alliance Auth](https://gitlab.com/allianceauth/allianceauth).

[![PyPi](https://img.shields.io/pypi/v/allianceauth-discordbot?color=green)](https://pypi.org/project/allianceauth-discordbot/)

## Features

* Bot Framework, easily extensible with more Cogs
* Integration with Alliance Auth, able to fetch data directly from its django project.
* Channel/Direct messaging feature, with Tasks and a Queue/Consumer
* Current Cogs
  * About
    * !about - Bot Information and Statistics
  * Auth
    * !auth or /auth - A direct link to the Auth Install to catch users familiar with other bots.
  * Members
    * !lookup [search string] - Fetch a users Main, Affiliation, State, Groups and linked characters from any character.
    * !altcorp [search string] - search for users with characters in an altcorp
  * Remind
    * !remindme [5s/m/h/d text] - Sets a simple non-persistent reminder timer when the bot will respond with the text
  * Sov
    * !vuln [context] - Returns a list of Vulnerable sov structures for a Region/Constellation/Solar_System or alliance
    * !sov [context] - Returns a list of _all_ sov structures for a Region/Constellation/Solar_System or alliance
    * !lowadm - Lists sov in need of ADM-ing, context provided in settings.
  * Time
    * !time or /time - Returns the current EVE Time.
  * Timers
    * !timer - Returns the next Structure timer from allianceauth.timerboard.
  * Ticket
    * /help and Message context command to create private support threads
  * PriceCheck:
    * amarr - Check an item price on Amarr market
    * jita -  Check an item price on Jita market
    * price - Check an item price on Jita and Amarr market
  * Easter Eggs,
    * !happybirthday [text] - Wishes the text a happy birthday, works with user mentions
  * WelcomeGoodbye
    * Welcome - Responds to user join events with predefined messages.
    * Goodbye - Responds to user leave events with predefined messages.
  * Admin
    * Slash commands to help with setting up a discord server when you are not admin or owner.
    * accessed via `/admin [command]`
    * add_role / add_role_read / rem_role - add/remove a role to a channel
    * new_channel - create a new channel and assign it a role for read access
    * promote_role_to_god/demote_role_to_god - promote/demote a role to/from full admin so for when you need it
    * empty_roles - list all roles on server with no members
    * clear_empty_roles - remove all empty roles from the server
    * orphans - find any user in discord with no auth user attached
    * get_webhooks - returns any webhooks setup in this current channel, or creates one for you and returns that
    * uptime - how long the bot has been up for

## Installation

* Ensure you have installed and configured the Alliance Auth Discord Service, <https://allianceauth.readthedocs.io/en/latest/features/services/discord.html>

* Update your [Discord Developer Application](https://discord.com/developers/applications) to include the Privileged Intents that we call. Please enable all intents.

![screenshot](https://i.imgur.com/A1yA24P.png)

* Install the app with your venv active

```bash
pip install allianceauth-discordbot
```

* Add `'aadiscordbot',` to your INSTALLED_APPS list in local.py.

* Add the below lines to your `local.py` settings file, Changing the contexts to yours.

```python
## Settings for Allianceauth-Discordbot
# Admin Commands
ADMIN_DISCORD_BOT_CHANNELS = [111, 222, 333]
# Sov Commands
SOV_DISCORD_BOT_CHANNELS = [111, 222, 333]
# Adm Commands
ADM_DISCORD_BOT_CHANNELS = [111, 222, 333]

DISCORD_BOT_SOV_STRUCTURE_OWNER_IDS = [1000169] # Centre for Advanced Studies example
DISCORD_BOT_MEMBER_ALLIANCES = [111, 222, 333] # A list of alliances to be considered "Mains"

DISCORD_BOT_ADM_REGIONS = [10000002] # The Forge Example
DISCORD_BOT_ADM_SYSTEMS = [30000142] # Jita Example
DISCORD_BOT_ADM_CONSTELLATIONS = [20000020] # Kimitoro Example

PRICE_CHECK_HOSTNAME = "evepraisal.com" # Point to your favorite evepraisal
```

```python
## Insert AADiscordBot's logging into Django Logging config
LOGGING['handlers']['bot_log_file']= {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'log/discord_bot.log'),
            'formatter': 'verbose',
            'maxBytes': 1024 * 1024 * 5,
            'backupCount': 5,
        }
LOGGING['loggers']['aadiscordbot'] = {'handlers': ['bot_log_file'],'level': 'DEBUG'}
```

* Add the below lines to `myauth/celery.py` somewhere above the `app.autodiscover_tasks...` line

```python

## Route AA Discord bot tasks away from AllianceAuth
app.conf.task_routes = {'aadiscordbot.tasks.*': {'queue': 'aadiscordbot'}}
```

* Run migrations `python manage.py migrate` (There should be none from this app)
* Gather your static files `python manage.py collectstatic` (There should be none from this app)

* Fetch `bot_conf.py` from the Git Repo into the root of your AA install, beside `manage.py`

```bash
wget https://raw.githubusercontent.com/pvyParts/allianceauth-discordbot/master/bot_conf.py
```

## Running Discordbot with Docker

* To download the `bot_conf.py` file into your `conf/` folder, run the following from your aa-docker folder
```bash
wget https://raw.githubusercontent.com/pvyParts/allianceauth-discordbot/master/bot_conf.py -O conf/bot_conf.py
```
* Update base image to have bot_conf.py mapped

```dockerfile
x-allianceauth-base:

# image: ${AA_DOCKER_TAG?err}

  &allianceauth-base
  build:
    context: .
    dockerfile: custom.dockerfile
    args:
      AA_DOCKER_TAG: ${AA_DOCKER_TAG?err}
  restart: always
  env_file:
    - ./.env
  volumes:
...
    - ./conf/bot_conf.py:/home/allianceauth/myauth/bot_conf.py
...
```

Add a service to run the Discordbot

```dockerfile
  allianceauth_discordbot:
    container_name: allianceauth_discordbot
    <<: [ *allianceauth-base ]
    restart: on-failure:1
    entrypoint: [ "python", "/home/allianceauth/myauth/bot_conf.py" ]
```

## Running DiscordBot with Supervisor

* Amend your supervisor.conf, correcting paths as required and add `authbot` to the launch group at the end of the conf

```ini
[program:authbot]
command=/home/allianceserver/venv/auth/bin/python /home/allianceserver/myauth/bot_conf.py
directory=/home/allianceserver/myauth
user=allianceserver
numprocs=1
autostart=true
autorestart=true
stopwaitsecs=600
stdout_logfile=/home/allianceserver/myauth/log/authbot.log
stderr_logfile=/home/allianceserver/myauth/log/authbot.log
```

```ini
#This block should already exist, add authbot to it
[group:myauth]
programs=beat,worker,gunicorn,authbot
priority=999
```

Go to admin and configure your admin users in the bot config model.

> Enable groups/states/users to utilize the lookup command by adding permissions under **corputils | corp stats |**

```ini
corputils.view_alliance_corpstats
```

## Optional Settings

### Built in Cogs
```python
# Change the bots default Cogs, add or remove if you want to use any of the extra cogs.

DISCORD_BOT_COGS = [
  "aadiscordbot.cogs.about", # about the bot
  "aadiscordbot.cogs.admin", # Discord server admin helpers
  "aadiscordbot.cogs.members", # Member lookup commands
  "aadiscordbot.cogs.timers", # timer board integration
  "aadiscordbot.cogs.auth", # return auth url
  "aadiscordbot.cogs.sov", # some sov helpers
  "aadiscordbot.cogs.time", # whats the time Mr Eve Server
  "aadiscordbot.cogs.eastereggs", # some "fun" commands from ariel...
  "aadiscordbot.cogs.remind", # very Basic in memory reminder tool
  "aadiscordbot.cogs.reaction_roles", # auth group integrated reaction roles
  "aadiscordbot.cogs.services", # service activation data
  "aadiscordbot.cogs.price_check", # Price Checks
  "aadiscordbot.cogs.eightball", # 8ball should i install this cog
  "aadiscordbot.cogs.welcomegoodbye", # Customizable user join/leave messages
  "aadiscordbot.cogs.models", # Populate and Maintain Django Models for Channels and Servers
  "aadiscordbot.cogs.quote", # Save and recall messages
  "aadiscordbot.cogs.prom_export", # Admin Level Logging cog
  "aadiscordbot.cogs.tickets", # Private thread ticket system with pingable groups.
  "aadiscordbot.cogs.recruit_me", # Private thread recruitment ticket system.
  ]
```

### Additional Rate Limiting

```python
# configure the optional rate limited
# this is a bot_task function and how many / time period
# 100/s equates to 100 per second max
# 10/m equates to 10 per minute or 1 every 6 seconds max
# 60/h equates to 60 per hour or one per minute max
DISCORD_BOT_TASK_RATE_LIMITS = {
        "send_channel_message_by_discord_id": "100/s",
        "send_direct_message_by_discord_id": "1/s",
        "send_direct_message_by_user_id": "1/s"
        }
```

## Reaction Roles
>
> ❗❗❗ **This will bypass the Group Leadership/Join Request System**: This is intended for open groups but not limited to it! ❗❗❗

The bot is able to run a reaction roles system that is compatible with auth and public users on a discord.

* If a member is part of auth it will do auth syncing of roles
* If a member is not found in auth and the reaction role message has the public flag set it will assign roles to anyone who reacts

### How To Reaction Role

 1. Setup the inital Message you wish to use buy using the command `!rr`

    * _Optional_ Edit the name and settings of this message in `Admin > Discord Bot > Reaction Role Messages`

 2. React to the message with the reactions you wish to use.
 3. The bot will counter react to the reactions when it creates the binding in auth.
 4. Goto `Admin > Discord Bot > Reaction Role Bindings`
 5. Assign the groups you want for each reaction

#### Messages Admin

![https://cdn.discordapp.com/attachments/639369068930924546/936082605156237332/unknown.png](https://cdn.discordapp.com/attachments/639369068930924546/936082605156237332/unknown.png)

#### Reactions Admin

![https://cdn.discordapp.com/attachments/639369068930924546/936084126379962378/unknown.png](https://cdn.discordapp.com/attachments/639369068930924546/936084126379962378/unknown.png)

## Integrations

* [Statistics](https://github.com/pvyParts/aa-statistics)
  * Adds zkill Monthly/Yearly stats to !lookup
* [timezones](https://github.com/ppfeufer/aa-timezones)
  * Updates the `time` command to have all timezones configured in auth.

## Welcome Messaages

`
With the WelcomeGoodbye Cog activated, Discordbot will grab a random message from the Welcome or Goodbye Message Model and send it to the Guild System channel

These can be configured in admin under `/admin/aadiscordbot/welcomemessage/` and `/admin/aadiscordbot/goodbyemessage/`

The messages support some string formatting

* `{user_mention} - A Discord @ Mention
* `{guild_name} - The name of the Discord Server
* `{auth_url} - A link to Auth

```text
Welcome {user_mention} to {guild_name}, I hope you enjoy your stay.

You can Authenticate for more access {auth_url}
```

## Private Thread Ticket System

> ❗❗❗ **While this is fully functional, this is still in early stages of development, Please report any issues you find!** ❗❗❗

With the `aadiscordbot.cogs.tickets` Cog activated, users wll be able to issue the `/help` command to pick a group to get help from.

The groups available for selection are configurable in the site admin under
`Discord Bot > Ticket Cog Configuration`

You also need to choose a channel to create the threads in from the site admin `Discord Bot > Ticket Cog Configuration`:

* Anyone who can use the `/help` command must have View and Send Message permissions on this channel otherwise they will not be able to see the tickets authbot creates for them
* Authbot must have the permissions to create private threads in this channel
* Authbot must have the permissions to send messages to this channel

## Using AA-Discordbot from my project

### Send Messages

You can use the send_message helper to send a message with text/embed to:

* Discord user_id
* Discord channel_id
* Auth User Model Object
* Auth user_pk

[aadiscordbot/tasks.py](https://github.com/pvyParts/allianceauth-discordbot/blob/master/aadiscordbot/tasks.py)

### Example Usage

```python
from django.contrib.auth.models import User
from django.apps import apps

## Use a small helper to check if AA-Discordbot is installs
def discord_bot_active():
    return apps.is_installed('aadiscordbot')

## Only import it, if it is installed
if discord_bot_active():
    from aadiscordbot.tasks import send_message
    # if you want to send discord embed import them too.
    from discord import Embed, Color

## this helper can be called to Queue up a Message
## AA Should not act on these, only AA-DiscordBot will consume them
if discord_bot_active():
    usr = User.objects.get(pk=1)

    # discord ID of user
    msg = "Channel ID Tests"
    e = Embed(title="Channel ID Tests!",
              description="This is a Test Embed.\n\n```Discord Channel ID```",
              color=Color.yellow())
    e.add_field(name="Test Field 1", value="Value of some kind goes here")
    send_message(channel_id=639252062818926642, embed=e) # Embed
    send_message(channel_id=639252062818926642, message=msg) # Message
    send_message(channel_id=639252062818926642, message=msg, embed=e) # Both

    # Discord ID of channel
    msg = "User ID Tests"
    e = Embed(title="User ID Tests!",
              description="This is a Test Embed.\n\n```Discord User ID```",
              color=Color.nitro_pink())
    e.add_field(name="Test Field 1", value="Value of some kind goes here")

    send_message(user_id=318309023478972417, embed=e) # Embed
    send_message(user_id=318309023478972417, message=msg) # Message
    send_message(user_id=318309023478972417, message=msg, embed=e) # Both

    # User model
    msg = "Auth User Model Tests"
    e = Embed(title="Auth User Model Tests!",
              description="This is a Test Embed.\n\n```Auth User Model```",
              color=Color.dark_orange())
    e.add_field(name="Test Field 1", value="Value of some kind goes here")
    send_message(user=usr, embed=e) # Embed
    send_message(user=usr, message=msg) # Message
    send_message(user=usr, message=msg, embed=e) # Both

    # User PK id
    msg = "Auth User PK Tests"
    e = Embed(title="Auth User PK Tests!",
              description="This is a Test Embed.\n\n```Auth User PK```",
              color=Color.brand_green())
    e.add_field(name="Test Field 1", value="Value of some kind goes here")
    send_message(user_pk=1, embed=e) # Embed
    send_message(user_pk=1, message=msg) # Message
    send_message(user_pk=1, message=msg, embed=e) # Both

    # Mixture of all of the above
    msg = "All Together Tests"
    e = Embed(title="All Together Tests!",
              description="This is a Test Embed.\n\n```All Together```",
              color=Color.blurple())
    e.add_field(name="Test Field 1", value="Value of some kind goes here")
    send_message(channel_id=639252062818926642,
                user_id=318309023478972417,
                user=User.objects.get(pk=1),
                message=msg,
                embed=e)
```

### Registering 3rd Party Cogs (Handling Commands)

In `auth_hooks.py`, define a function that returns an array of cog modules, and register it as a `discord_cogs_hook`:

```python
@hooks.register('discord_cogs_hook')
def register_cogs():
    return ["yourapp.cogs.cog_a", "yourapp.cogs.cog_b"]
```

## Optional Settings continued

### Isolate AuthBot from Auth's Discord Service

```python
AUTHBOT_DISCORD_APP_ID = 'App ID for dedicated bot'
AUTHBOT_DISCORD_BOT_TOKEN = 'Token for dedicated bot'
```

## Issues

Please remember to report any aa-discordbot related issues using the issues on **this** repository.

## Troubleshooting

### Py-Cord and discord.py fighting in venv

**Problem:**

Something has gone funny with my venv after i installed another app that wanted `discord.py`

**Reason:**

This is due to the Py-cord lib sharing the `discord` namespace. Py-Cord is however a drop in replacement. So no issues should arise from using it over the now legacy discord.py lib. **YMMV**

**Fix:**

 1. Uninstall `discord.py` by running `pip uninstall discord.py` with your venv active.
 2. Reinstall `py-cord` by running `pip install -U py-cord==2.0.0b3` with your venv active.
 3. Approach the dev from the app that overrode your py-cord to update to a maintained lib.
