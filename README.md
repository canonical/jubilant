# Jubilant, the joyful library for integration-testing Juju charms

PR TEST FOR WEBHOOK!

Jubilant is a Python library that wraps the [Juju](https://juju.is/) CLI for use in charm integration tests. It provides methods that map 1:1 to Juju CLI commands, but with a type-annotated, Pythonic interface.

It was written to supersede the use of [pytest-operator](https://github.com/charmed-kubernetes/pytest-operator) and [python-libjuju](https://github.com/juju/python-libjuju/) for charm integration tests. Python-libjuju in particular has a complex and confusing API, and its use of `async` is unnecessary for testing.

**NOTE:** Jubilant is in very early stages of development. This is pre-alpha code. Our intention is to release a 1.0.0 version early to mid 2025.


## Design goals

- Match the Juju CLI. We try to ensure methods, argument names, and response field names match the Juju CLI and its responses, with minor exceptions (such as "application" being shortened to "app" in `Status` fields).
- Simple API. Higher-level operations will be in helpers and fixtures, not the main `Juju` class.
- No `async`. This was a "feature" of python-libjuju that isn't desired for integration tests.
- Support Juju 3 and 4. The Juju team is guaranteeing CLI arguments and `--format=json` responses won't change between Juju 3.x and 4.x. When Juju 5.x arrives and changes the CLI, we'll keep the Jubilant API simple and 1:1 with the 5.x CLI, but will consider adding a `jubilant.compat` layer to avoid tests have to manually work around differences between 4.x and 5.x.
