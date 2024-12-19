# Jubilant, the joyful library for integration-testing Juju charms

Jubilant is a Python library that wraps the [Juju](https://juju.is/) CLI for use in charm integration tests. It provides methods that map 1:1 to Juju CLI commands, but with a type-annotated, Pythonic interface.

**NOTE:** Jubilant is in very early stages of development. This is pre-alpha code. Our intention is to release a 1.0.0 version early to mid 2025.


## Design goals

- Familiar to users of the Juju CLI. We try to ensure methods, argument names, and response field names match the Juju CLI and its responses, with minor exceptions (such as "application" being shortened to "app" in `Status` fields).
- Simple API. Any cleverness in helpers and fixtures.
- TODO: versioning (Juju 3 and 4, maybe jubilant.compat for Juju 5 changes)
- TODO: no async/await
