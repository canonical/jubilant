# Design goals

We designed Jubilant so it would:

- **Match the Juju CLI.** Method, parameter, and response field names match the Juju CLI, with minor exceptions (such as "application" being shortened to "app").
- **Have a simple API.** Higher-level operations will be in helper functions, not the main `Juju` class (the only exception being `Juju.wait`).
- **Not use `async`.** This was a "feature" of python-libjuju that adds complexity and isn't needed for integration tests. In addition, most Juju CLI commands return quickly and complete asynchronously in the background.
- **Support Juju 3 and 4.** The Juju team is guaranteeing CLI arguments and `--format=json` responses won't change between Juju 3.x and 4.x. When Juju 5.x arrives and changes the CLI, we'll keep the Jubilant API simple and match the 5.x CLI. However, we will consider adding a compatibility layer to avoid tests having to manually handle differences between 4.x and 5.x.
