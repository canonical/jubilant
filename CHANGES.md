# 1.9.0 - 29 April 2026

## Features

* Implement add_cloud and update_cloud methods (#283)

## Fixes

* Correct behaviour when transparently handling Juju's snap confinement (#275)

## Documentation

* Restructure homepage and update intro to Jubilant (#287)

## CI

* Configure dependabot (#288)
* Pin the versions of zizmor and codespell when run by pre-commit (#303)
* Fix unit runs-on (#302)
* Run CI (especially integration tests) every Monday morning (#301)

# 1.8.0 - 30 March 2026

## Breaking Changes

* Respect self.model in offer method (#276)

## Features

* Allow metadata_source to be passed down to the CLI via the bootstrap command (#272)

## Documentation

* WaitError is raised when error is true, not false. (#256)
* Consistent markup for "true" and "false" (#254)
* Include a directive for documentation in AGENTS.md (#268)
* Replace juju.is links and change link in docs header (#267)
* Remove pytest-operator migration guide (moved to Ops docs) (#270)
* Fix docstring of consume() (#269)
* Refocus tutorial on standalone usage (#280)

## Tests

* Remove requests dependency (#262)

## Refactoring

* Add the ssh key earlier, so that no retry is needed (#264)

## CI

* Correct copilot-collections permissions so that the job can create a PR if needed (#253)
* Add Zizmor workflow, fix test_secrets ordering (#274)

# 1.7.0 - 29 January 2026

## Features

* Treat running an invalid action in Juju 4 the same way as Juju 3 (#245)
* Add model_constraints method to get/set machine constraints (#236)
* Provide additional arguments for model destruction (#243)

## Documentation

* Make homepage more consistent with Ops (#237)

## Refactoring

* Simplify _format_config, implement _format_constraint with it (#250)

## CI

* Test against Juju 4.0.0 (#232)
* Install Copilot files from the copilot-collections tool (#242)

# 1.6.2 - 17 December 2025

## Fixes

* Fix Version.__str__ and strictify parsing (#230)

## Refactoring

* Simplify comprehensions in statustypes and modeltypes (#234)

## CI

* Fix "ty" type checking issues (#235)

# 1.6.0 - 20 November 2025

## Features

* Add SecretURI.__repr__ to make type obvious in error messages (#213)
* Add version command (#219)
* Copy files to juju-accessible place for deploy, refresh, scp (#207)
* Add show-model command (#218)
* Add add-credential command (#221)
* Add SSH key management commands (add-ssh-key, remove-ssh-key) (#228)

## Fixes

* Support "app/leader" unit syntax for run and exec (#216)
* Change machine parameter type to int | str in Juju.exec (#223)

## Documentation

* Use 'integration' group in CI example (#209)
* Improve docs for wait logging and debug_log (#208)
* Correct defaults for exec and run "wait" parameters (#210)
* Jubilant is not *just* for charm integration tests (#215)

## CI

* Fix spell checking (#225)

# 1.5.0 - 10 October 2025

## Fixes

* Add timeout to temp_model destroy-model to fix microk8s issues (#188)
* Allow revealed secrets without checksums (#204)

## Documentation

* Update tutorial with info about deploying .charm files (#187)
* Another wait() example, and link to it from ref and how-to (#195)
* Add docstrings to common status classes and attributes (#196)

## Doc

* Mention 'timeout' argument unit in `wait` method docstring (#190)

# 1.4.0 - 26 August 2025

## Features

* Add bootstrap command (#180)

## Documentation

* Add a security explanation doc (#173)
* Update links and config for switch to documentation.ubuntu.com/jubilant (#174)
* Be more confident about no breaking changes after 1.0 (#175)
* Add sitemap.xml, add new spelling check, remove markdown lint (#177)
* Add Google Analyics integration and cookie consent banner (#181)

# 1.3.0 - 24 July 2025

## Features

* Add "overlays" parameter to Juju.deploy (#160)
* Add consume command (#164)
* Support multiple controllers (#165)
* Have temp_model forward "cloud" and other args to add_model (#168)
* Secret management (#135)

## Documentation

* Add an example of temp_model, including how to set attributes (#162)

## CI

* Move TIOBE workflow to self-hosted runners (#167)
* Fix installing TIOBE dependencies on the self-hosted runners (#169)

# 1.2.0 - 12 June 2025

## Features

* Add Status.get_units, include subordinates in all_* and any_* (#150)

## CI

* Add reporting to TIOBE (#149)

# 1.1.1 - 05 June 2025

## Fixes

* "juju model" doesn't use --model argument (#148)

# 1.1.0 - 03 June 2025

## Features

* Allow specifying cloud when creating model (#143)

# 1.0.1 - 30 April 2025

## Fixes

* Fix format of --bind argument for deploy (#132)

# 1.0.0 - 29 April 2025

## Breaking Changes

* In "offer", move endpoint to keyword-only arg instead of *args (#126)
* Make "reset" an explicit arg for config/model_config (#125)

## Features

* Add "bind" argument to deploy() (#121)
* Deploy a temp model into a specified controller (#124)
* Add all_agents_idle helper (#127)

# 0.5.0 - 24 April 2025

## Breaking Changes

* Change all_* and any_* to take *apps instead of a list (#116)
* Return data rather than raising an exception on status-error (#120)

## Features

* Add scp command (#109)
* Add model-config command (#115)
* Add add_secret method (#112)

## Fixes

* Log wait status diffs under jubilant.wait logger name (#110)
* Correct polarity of WaitError message (#113)

## Tests

* Add machine integration tests (LXD) (#103)

## CI

* Test deploy with resources (and base) (#108)

# 0.4.1 - 15 April 2025

## Features

* Add refresh command (#93)
* Slightly more helpful TaskError.__str__ (#99)

## Documentation

* Fix and->or in all_* docstrings (#96)
* Add "How to migrate from pytest-operator to Jubilant" (#98)

# 0.4.0 - 10 April 2025

## Breaking Changes

* Change remove_unit to use *args (#89)

## Features

* Add remove_application method (#86)
* Add offer command (#82)
* Add ssh command (#92)

## Fixes

* Don't log "juju status" calls in Juju.wait() (#88)

## Documentation

* Minor rewording in docstring of remove_unit method (#87)

# 0.3.2 - 07 April 2025

## Features

* Add "stdin" parameter to Juju.cli (#83)

# 0.3.1 - 07 April 2025

## Features

* Condense Juju.wait status logging by using gron-style diff (#79)
* Add trust command (#81)

# 0.3.0 - 04 April 2025

## Fixes

* Allow the library to work on Python 3.8+ (#80)

# 0.2.1 - 03 April 2025

## Features

* Add "wait" argument to exec and run (#77)
* Add remove_relation method (#78)

# 0.2.0 - 03 April 2025

## Breaking Changes

* Rename deploy param resource -> resources (#74)
* Add exec method (#66)

## Documentation

* Flesh out landing page and add tutorial (#61)
* Make example fixtures module-scoped, explain Python 3.12 requirement (#65)
* Add 'charmcraft pack' in sample GitHub action (#69)
* Change Juju links to point to latest doc site (#76)

## Tests

* Add integration test of run (action) fail and exception (#67)

# 0.1.0 - 21 March 2025

## Documentation

* Set maximum_signature_line_length to 80 (#60)
* Flesh out README.md (#59)

# 1.0.0b3 - 20 March 2025

## CI

* Fix publish environment (#58)
* Bump beta version

# 1.0.0b2 - 20 March 2025

## Features

* Add RunError, move Juju class to _juju.py
* Get basic Sphinx docs working locally (#3)
* Rename wait_status to wait and adjust the API (#2)
* Add generated status dataclasses (#26)
* Add config method (#39)
* Add run method (#42)
* Add integrate method (#45)
* Add remove_unit method (#47)
* Add add_unit method (#46)
* Pretty-print Status dataclass (#37)
* Add test helpers and run integration tests in CI (#49)
* Add basic integration tests for most jubilant.Juju methods (#53)
* Workflow and metadata for publishing to PyPI (#55)

## Fixes

* Add additional params to deploy() (#23)

## Documentation

* Add README
* Use Canonical documentation starter pack (#36)

## Tests

* Add unit tests of existing functionality (#34)

## Refactoring

* Move error classes to where they're raised (#27)
* Move types.py to statustypes.py to avoid confusion with stdlib (#28)

## CI

* Add GitHub Actions for unit tests, linting, static type checking (#32)
* Single ci.yaml, fmt -> format, tweak lint (#33)

## Build

* Allow ARGS='additional args' for (some) Makefile commands (#54)
