# Jubilant

```{toctree}
:maxdepth: 2
:hidden: true

Tutorial <tutorial/getting-started>
how-to/index
reference/index
explanation/index
```

Jubilant is a Python library that wraps the [Juju](https://juju.is/) CLI for use in charm integration tests. It provides methods that map 1:1 to Juju CLI commands, but with a type-annotated, Pythonic interface.

You should consider switching to Jubilant if your integration tests currently use [pytest-operator](https://github.com/charmed-kubernetes/pytest-operator) (and they probably do). Jubilant has an API you'll pick up quickly, and it avoids some of the pain points of [python-libjuju](https://github.com/juju/python-libjuju/), such as websocket failures and having to use `async`. Read our [design goals](explanation/design-goals).

Jubilant is currently in pre-release or "beta" phase (see [PyPI releases](https://pypi.org/project/jubilant/)). Our intention is to release version 1.0.0 in May 2025.


The library provides:

- The main [](jubilant.Juju) class, with methods such as [`deploy`](jubilant.Juju.deploy) and [`integrate`](jubilant.Juju.integrate)
- The [`Juju.wait`](jubilant.Juju.wait) method, which waits for a condition such as "all apps active"
- Status helpers such as [](jubilant.all_active), for use with `Juju.wait`
- Context managers such as [](jubilant.temp_model), for use in test setup and teardown


## In this documentation

````{grid} 1 1 2 2
```{grid-item-card} [Tutorial](tutorial/getting-started)
**Start here**: a hands-on introduction to Jubilant, including how to write a charm integration test
```

```{grid-item-card} [How-to guides](how-to/index)
**Step-by-step guides** covering key operations and common tasks
- [Migrate from pytest-operator](how-to/migrate-from-pytest-operator)
```
````

````{grid} 1 1 2 2
:reverse:
```{grid-item-card} [Reference](reference/index)
**Technical information**
- [API reference](reference/jubilant)
```

```{grid-item-card} [Explanation](explanation/index)
**Discussion and clarification** of key topics
- [Design goals](explanation/design-goals)
```
````


## Releases

[Jubilant releases](https://github.com/canonical/jubilant/releases) are tracked on GitHub, and use [semantic versioning](https://semver.org/). To get notified when there's a new release, watch the [Jubilant repository](https://github.com/canonical/jubilant).


## Project and community

Jubilant is free software and released under the [Apache license, version 2.0](https://www.apache.org/licenses/LICENSE-2.0).

The Jubilant project is sponsored by [Canonical Ltd](https://www.canonical.com).

- [Code of conduct](https://ubuntu.com/community/ethos/code-of-conduct)
- [Contribute to the project](https://github.com/canonical/jubilant?tab=readme-ov-file#contributing-and-developing)
- [Development](https://github.com/canonical/jubilant?tab=readme-ov-file#contributing-and-developing): how to make changes to Jubilant and run its tests
