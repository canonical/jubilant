# Jubilant

```{toctree}
:maxdepth: 2
:hidden: true

Tutorial <tutorial/getting-started>
reference/index
explanation/index
```

Jubilant is a Python library that wraps the [Juju](https://canonical.com/juju) CLI, primarily for use in charm integration tests.

When writing charm integration tests, use Jubilant with `pytest-jubilant`. See {external+operator:ref}`How to write integration tests for a charm <write-integration-tests-for-a-charm>` in the Ops documentation. Ops also has several [demo charms](https://github.com/canonical/operator/tree/main/examples) that you can experiment with. The demo charms use Jubilant in their integration tests.

Jubilant's methods map 1:1 to Juju CLI commands and have a type-annotated, Pythonic interface:

- The main [](jubilant.Juju) class, with methods such as [`deploy`](jubilant.Juju.deploy) and [`integrate`](jubilant.Juju.integrate)
- The [`Juju.wait`](jubilant.Juju.wait) method, which waits for a condition such as "all apps active"
- Status helpers such as [](jubilant.all_active), for use with `Juju.wait`
- Context managers such as [](jubilant.temp_model), for use in test setup and teardown

You should switch to Jubilant if your integration tests currently use [pytest-operator](https://github.com/charmed-kubernetes/pytest-operator). Jubilant avoids some of the pain points of [python-libjuju](https://github.com/juju/python-libjuju/), such as websocket failures and having to use `async`.

## In this documentation

- [Getting started with Jubilant](tutorial/getting-started)
- [Design goals](explanation/design-goals)
- [API reference](reference/jubilant)

This documentation uses the [Diátaxis documentation structure](https://diataxis.fr/).

## Releases

[Jubilant releases](https://github.com/canonical/jubilant/releases) are tracked on GitHub, and use [semantic versioning](https://semver.org/). To get notified when there's a new release, watch the [Jubilant repository](https://github.com/canonical/jubilant).

## Project and community

Jubilant is a member of the Ubuntu family. It's an open source project ([Apache license](https://www.apache.org/licenses/LICENSE-2.0)) that warmly welcomes community contributions, suggestions, fixes and constructive feedback.

- [Report a bug](https://github.com/canonical/jubilant/issues)
- [Contribute](https://github.com/canonical/jubilant?tab=readme-ov-file#contributing-and-developing)
- [Code of conduct](https://ubuntu.com/community/ethos/code-of-conduct)

For support, join [Charm Development](https://matrix.to/#/#charmhub-charmdev:ubuntu.com) on Matrix. You'll be able to chat with the maintainers of Jubilant (the Canonical Charm Tech team) and a friendly community of charm developers!

To follow along with updates and tips about charm development, join our [Discourse forum](https://discourse.charmhub.io/).
