# aa-discordbot

aa-discordbot for [Alliance Auth](https://gitlab.com/allianceauth/allianceauth).

## Features

* Bot Framework, easily extensible with more Cogs
* Integration with Alliance Auth, able to fetch data directly from its django project.
* Current Cogs
  * !about - Bot Information and Statistics
  * Auth
    * !auth - A direct link to the Auth Install to catch users familiar with other bots.
    * !orphans - Returns a list of users on this server, who are not known to AA
  * !timers - The next upcoming timer
  * !lookup - Fetch a users Main, Affiliation, State, Groups and linked characters from any character.

## Installation

* Install the app with your venv active

```bash
pip install `pip install -U git+https://github.com/pvyParts/allianceauth-discordbot.git`
```

* Add `'aa-discordbot',` to your INSTALLED_APPS list in local.py.

* Add the below lines to your `local.py` settings file, Changing the channel IDs to yours.

 ```python
## Settings for Allianceauth-Discordbot
DISCORD_BOT_ADMIN_USER = 140706470856622080 #UserID of the Discord Admin, used for superadmin stuff
# Admin Commands
ADMIN_DISCORD_BOT_CHANNELS = 111,222,333
# Sov Commands
SOV_DISCORD_BOT_CHANNELS = 111,222,333
# Adm Commands
ADM_DISCORD_BOT_CHANNELS = 111,222,333

DISCORD_BOT_SOV_STRUCTURE_OWNER_IDS = [1000169] # Centre for Advanced Studies example
DISCORD_BOT_MEMBER_ALLIANCES = 111,222,333 # A list of alliances to be considered "Mains"

DISCORD_BOT_ADM_REGIONS = [10000002] # The Forge Example
DISCORD_BOT_ADM_SYSTEMS = [30000142] # Jita Example
DISCORD_BOT_ADM_CONSTELLATIONS = [20000020] # Kimitoro Example
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

```
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

```
#This block should already exist, add authbot to it
[group:myauth]
programs=beat,worker,gunicorn,authbot
priority=999
```


## Issues

Please remember to report any aa-discordbot related issues using the issues on **this** repository.
