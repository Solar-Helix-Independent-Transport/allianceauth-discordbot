# aa-discordbot

aa-discordbot for [Alliance Auth](https://gitlab.com/allianceauth/allianceauth).

## Installation

**Python 3.5.3 or higher is required**

With your venv active,

pip install `pip install -U git+https://github.com/pvyParts/allianceauth-discordbot.git`

pip install requirements
```
discord.py
pendulum
aioredis
aiohttp
```
Add `'aa-discordbot',` to your local.py, run migrations a restart auth.

create a new file in your auth project file `bot_conf.py` in the same directory as the manage.py file
copy the contents of the bot_conf.py file from in the root of the repo

amend your supervisor.conf, update paths as req'd and add `authbot` to the launch group at the end of the conf

to include
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


## Issues

Please remember to report any aa-discordbot related issues using the issues on **this** repository.
