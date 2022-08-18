# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## [3.2.0]

### New
* Reworked the task consumer to alow tasks to persist a gracefull restart
- Added a configurable global rate limit option on tasks

## [3.1.2]

### New
* Added ability to run bot on its own tokens

## [3.1.1]

### Fixes
* Added very verbose logging to any startup errors
+ Added a 2 min cool down on hard failures at startup

## [3.1.0]

### Added
* Updated Discord lib
+ Added startup checks to ensure admins know if there is an iuus with their bot
+ Moved more commands to slash

## [3.0.1] - [3.0.5]
+ Updated things, fixed odd bugs

## [3.0.0]

### Added
* Moved to new Discord library
+ Swapped many commands to Slash
+ Full Reaction Roles support with public member access

## [0.5.2] 2021-07-09

### Added
* More Permission Decorators
### Fixes
* Corrected a typo in the in_channel permissions decorater
## [0.5.1] 2021-07-09
### Added
* Allows Prefix to be set as a setting
### Fixed
* Documents all settings in readme
## [0.5.0] 2021-07-09
### Fixes
* Mostly internal changes
* Logging is cleaned and documented
* Permissions are moved into Decorators and consistent across all cogs (and can be used my others)
* All app settings are properly sanitized and defaulted
* Prefix and Access Denied reacc can be configured

## [0.4.0] 2021-05-05
### Added
* Price Check Cog, PR #40 (@ppfeufer)
### Fixes
* Use the Django Application Registry instead of reading INSTALLED_APPS, @ErikKalkoken

## [0.3.1] 2021-02-06
### Added
* Added PyPi Deployment stuffs
### Fixes
* Lookup cog doesnt throw error on not found. PR #33 (@ppfeufer)

## [0.3.0] 2021-02-05
First Non-Alpha Release, AA-Discord bot has been heavily tested by the community now, many thanks to all involved.
### Added
* App Cogs can now be customized to load external cogs
* New shiny Time cog, using AA-Timezones
### Fixes
* Use AA-Statistics, the rebranded authanalitics

### Docs
Notated Integrations
## [0.2.5a Alpha] 2021-01-05
### Fixes
* Readme reflects new settings formats
* Cogs are configurable by Settings
* Docker Support (again)
* Refactor Channel/Direct message tasks to be more AA aware, adds shims to old tasks.

## [0.2.4a Alpha] 2021-01-02
### Fixes
* Removes Click dependency for better Python 3.6 support
* Server model was returning invalid server_name as its string

## [0.2.1a Alpha] 2021-01-02
### Fixes
* Adds some logging

## [0.2.0a Alpha] 2021-01-02
The initial migration was edited here, be aware you might need to migrate zero before you update
### Added
* Documented all Cogs. Plenty changed here to polish them just read the readme...
* Adds tasks to send Direct and Private Messages
### Fixes
* Postgres Compatability
* Module Compatability, only imports features if they are installed.

## [0.1.13a PreRelease]
* A lot of things happened here, we suck at changelogs

## [0.0.2a1 PreRelease] - 2020-09-21

### Added
* !Auth Cog
* Requirements to Setup.py
* Install Documentation
