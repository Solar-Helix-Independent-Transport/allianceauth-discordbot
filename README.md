# AA-Discordbot

AA-Discordbot for [Alliance Auth](https://gitlab.com/allianceauth/allianceauth).

## Features

* Bot Framework, easily extensible with more Cogs
* Integration with Alliance Auth, able to fetch data directly from its django project.
* Channel/Direct messaging feature, with Tasks and a Queue/Consumer
* Current Cogs
  * About
    * !about - Bot Information and Statistics
    * !uptime - Shows the uptime of the bot
    * !get_webhooks - Get or create a webhook for the current channel and DM it to the requestor
    * !new_channel [category id] [channel name] - Create a new channel and close it to public access
    * !add_role [channel name] [role name] - Add a role to a channel
    * !rem_role [channel name] [role name] - Remove a role from a channel
  * Auth
    * !auth - A direct link to the Auth Install to catch users familiar with other bots.
    * !orphans - Returns a list of users on this server without a matched AA account.
  * !timers - The next upcoming timer
  * Members
    * !lookup - Fetch a users Main, Affiliation, State, Groups and linked characters from any character.
    * !altcorp [search string] - search for users with characters in an altcorp
  * Remind
    * !remindme [5s/m/h/d text] - Sets a simple non-persistent reminder timer when the bot will respond with the text
  * Sov
    * !vuln [context] - Returns a list of Vulnerable sov structures for a Region/Constellation/Solar_System or alliance
    * !sov [context] - Returns a list of _all_ sov structures for a Region/Constellation/Solar_System or alliance
    * !lowadm - Lists sov in need of ADM-ing, context provided in settings.
  * Time
    * !time - Returns the current EVE Time.
  * Timers
    * !timer - Returns the next Structure timer from allianceauth.timerboard.
  * Easter Eggs,
    * !happybirthday [text] - Wishes the text a happy birthday, works with user mentions

## Installation

* Update your [Discord Developer Application](https://discord.com/developers/applications) to include the Privileged Intents that we call. Please add Server Members and Presence (for future development).

![screenshot](https://imgur.com/3Sr4yFZ)

* Install the app with your venv active

```bash
pip install -U git+https://github.com/pvyParts/allianceauth-discordbot.git
```

* Add `'aadiscordbot',` to your INSTALLED_APPS list in local.py.

* Add the below lines to your `local.py` settings file, Changing the channel IDs to yours.

 ```python
## Settings for Allianceauth-Discordbot
DISCORD_BOT_ADMIN_USER = [140706470856622080] #This UserID is allowed to run any command
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
```
* Optional Settings
 ```python
# configure the bots cogs.
DISCORD_BOT_COGS =[ "cogs.about",
                    "cogs.members",
                    "cogs.timers",
                    "cogs.auth",
                    "cogs.sov",
                    "cogs.time",
                    "cogs.eastereggs",
                    "cogs.remind",]
```

* Add the below lines to `myauth/celery.py` somewhere above the `app.autodiscover_tasks...` line

```python

## Route AA Discord bot tasks away from AllianceAuth
app.conf.task_routes = {'aadiscordbot.tasks.*': {'queue': 'aadiscordbot'}}
```

* Run migrations `python manage.py migrate` (There should be none from this app)
* Gather your staticfiles `python manage.py collectstatic` (There should be none from this app)

* Fetch `bot_conf.py` from the Git Repo into the root of your AA install, beside `manage.py`

```bash
wget https://raw.githubusercontent.com/pvyParts/allianceauth-discordbot/master/bot_conf.py
```

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

## Using AA-Discordbot from my project
[aadiscordbot/tasks.py](https://github.com/pvyParts/allianceauth-discordbot/blob/master/aadiscordbot/tasks.py)

```python
## Use a small helper to check if AA-Discordbot is installs
def discord_bot_active():
    return 'aadiscordbot' in settings.INSTALLED_APPS

## Only import it, if it is installed
if app_discord_bot_active():
    import aadiscordbot.tasks

## These two tasks can be called to Queue up a Message
## AA Should not act on these, only AA-DiscordBot will consume them
if discord_bot_active():
    aadiscordbot.tasks.send_direct_message_by_user_id.delay(user_pk, message_content)
    aadiscordbot.tasks.send_channel_by_discord_id.delay(channel_id, message_content, embed=False)
```

## Issues

Please remember to report any aa-discordbot related issues using the issues on **this** repository.
