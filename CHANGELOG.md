# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

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
