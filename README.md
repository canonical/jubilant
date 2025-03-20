# Jubilant, the joyful library for integration-testing Juju charms

![CI Status](https://github.com/canonical/jubilant/actions/workflows/ci.yaml/badge.svg)

Jubilant is a Python library that wraps the [Juju](https://juju.is/) CLI for use in charm integration tests. It provides methods that map 1:1 to Juju CLI commands, but with a type-annotated, Pythonic interface.

It was written to supersede the use of [pytest-operator](https://github.com/charmed-kubernetes/pytest-operator) and [python-libjuju](https://github.com/juju/python-libjuju/) for charm integration tests. Python-libjuju in particular has a complex and confusing API, and its use of `async` is unnecessary for testing.

Jubilant is currently in pre-release or "beta" phase ([PyPI releases](https://pypi.org/project/jubilant/#history)). Our intention is to release a 1.0.0 final version in May 2025.

[**Read the full documentation.**](https://canonical-jubilant.readthedocs-hosted.com/)


## Using Jubilant

Jubilant is published to PyPI, so you can install and use it with your favourite Python package manager:

```
$ pip install jubilant
# or
$ uv add jubilant
```

To use Jubilant in Python code, instantiate a `Juju` instance and call methods like `deploy` and `wait`:

```python
import jubilant

juju = jubilant.Juju()
juju.deploy('snappass-test')
juju.wait(jubilant.all_active)
```

Below is an example integration test [from Jubilant itself](https://github.com/canonical/jubilant/blob/main/tests/integration/test_basic.py). This test uses the [`juju` pytest fixture](https://github.com/canonical/jubilant/blob/main/tests/integration/conftest.py), which adds a model during, runs your test with the `Juju` instance, and destroys the model during teardown:

```python
def test_deploy(juju: jubilant.Juju):
    juju.deploy('snappass-test')             # Deploy the charm
    status = juju.wait(jubilant.all_active)  # Wait till the app and unit are 'active'

    # Hit the Snappass HTTP endpoint to ensure it's up and running.
    address = status.apps['snappass-test'].units['snappass-test/0'].address
    response = requests.get(f'http://{address}:5000/', timeout=10)
    response.raise_for_status()
    assert 'snappass' in response.text.lower()
```

You don't have to use [Pytest](https://docs.pytest.org/en/stable/) with Jubilant, but it's what we usually recommend. Its fixtures and its simple `assert`-based approach make writing tests easy.


## Design goals

We designed Jubilant so it would:

- Match the Juju CLI. Method, parameter, and response field names match the Juju CLI, with minor exceptions (such as "application" being shortened to "app").
- Have a simple API. Higher-level operations will be in helpers and fixtures, not the main `Juju` class (the only exception being `Juju.wait`).
- Not use `async`. This was a "feature" of python-libjuju that adds complexity and isn't needed for integration tests.
- Support Juju 3 and 4. The Juju team is guaranteeing CLI arguments and `--format=json` responses won't change between Juju 3.x and 4.x. When Juju 5.x arrives and changes the CLI, we'll keep the Jubilant API simple and 1:1 with the 5.x CLI, but will consider adding a `jubilant.compat` layer to avoid tests have to manually work around differences between 4.x and 5.x.


## Contributing and developing

Anyone can contribute to Jubilant. It's best to start by [opening an issue](https://github.com/canonical/jubilant/issues) with a clear description of the problem or feature request, but you can also [open a pull request](https://github.com/canonical/jubilant/pulls) directly.

Jubilant uses [`uv`](https://docs.astral.sh/uv/) to manage Python dependencies and tools, and `make` to run development tasks, so you'll need to [install uv](https://docs.astral.sh/uv/#installation) to work on Jubilant.

After that, clone the Jubilant codebase and type `make all` to run various checks and the unit tests:

```
$ git clone https://github.com/canonical/jubilant
Cloning into 'jubilant'...
...
$ cd jubilant
$ make all
...
========== 107 passed in 0.26s ==========
```

To contribute a code change, write your fix or feature, add tests, document it, and run `make all` before you push and create a PR. Once you create a PR, GitHub will also run the integration tests, which takes several minutes.


## Doing a release

To create a new release of Jubilant:

- Update the `__version__` field in [`jubilant/__init__.py`](https://github.com/canonical/jubilant/blob/main/jubilant/__init__.py) to the new version you want to release.
- Push up a PR with this change and get it reviewed and merged.
- Create a [new release](https://github.com/canonical/jubilant/releases/new) on GitHub. The tag should be in format `v<__version__>`, for example `v1.0.0`.
- The [`publish.yaml` workflow](https://github.com/canonical/jubilant/blob/main/.github/workflows/publish.yaml) will automatically build the release and publish it to PyPI.
- Once the publish workflow has finished, check that the new version appears in the [PyPI version history](https://pypi.org/project/jubilant/#history).
