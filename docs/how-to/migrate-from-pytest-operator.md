# How to migrate from pytest-operator to Jubilant

Many charm integration tests use [pytest-operator](https://github.com/charmed-kubernetes/pytest-operator) and [python-libjuju](https://github.com/juju/python-libjuju). This guide explains how to migrate your integration tests from those libraries to Jubilant.

To get help while you're migrating tests, please keep the [API reference](/reference/jubilant) handy, and make use of your IDE's autocompletion features -- we've tried to provide good type annotations and docstrings.

Migrating your tests can be broken into three steps:

1. Updating your dependencies
2. Adding fixtures to `conftest.py`
3. Updating the tests themselves

Let's look at each of these in turn.


## Updating your dependencies

The first thing you'll need to do is add `jubilant` as a dependency to your `tox.ini` or `pyproject.toml` dependency list. Before Jubilant 1.0 is released, you should consider locking it to a specific version.

You can also remove the dependencies on `juju` (python-libjuju), `pytest-operator`, and `pytest-asyncio`.

The diff of your `tox.ini` might look something like this:

```diff
 [testenv:integration]
 deps =
     boto3
     cosl
-    juju>=3.0
+    jubilant==0.4.0
     pytest
-    pytest-operator
-    pytest-asyncio
     -r{toxinidir}/requirements.txt
```


## Adding fixtures to `conftest.py`

The pytest-operator library includes pytest fixtures, but Jubilant does not include any fixtures, so you'll need to add one or two fixtures to your tests's `conftest.py`.

### A `juju` model fixture

Jubilant expects that a Juju controler has already been set up, either using [Concierge](https://github.com/jnsgruk/concierge) or a manual approach. However, you'll want a fixture to create a temporary model. We recommend calling this `juju`:

```python
# tests/integration/conftest.py

import jubilant
import pytest

@pytest.fixture(scope='module')
def juju(request: pytest.FixtureRequest):
    keep_models = bool(request.config.getoption('--keep-models'))

    with jubilant.temp_model(keep=keep_models) as juju:
        juju.wait_timeout = 10 * 60

        yield juju  # run the test

        if request.session.testsfailed:
            log = juju.debug_log(limit=1000)
            print(log, end='')

def pytest_addoption(parser):
    parser.addoption(
        '--keep-models',
        action='store_true',
        default=False,
        help='keep temporarily-created models',
    )
```

In your tests, use the fixture as follows:

```python
# tests/integration/test_charm.py

def test_active(juju: jubilant.Juju):
    juju.deploy('mycharm')
    juju.wait(jubilant.all_active)
```

A few things to note:

* This adds a command-line parameter `--keep-models` (to match pytest-operator's). If that is set, the fixture keeps the temporary model around after running the tests.
* It sets [`juju.wait_timeout`](jubilant.Juju.wait_timeout) to 10 minutes, to match python-libjuju's default `wait_for_idle` timeout.
* If any of the tests fail, the fixture uses `juju.debug_log` to display the last 1000 lines of `juju debug-log` output.
* The fixture is module-scoped, like pytest-operator's `ops_test` fixture. This means that a new model is created for every `test_*.py` file, but not for every test.

### An application fixture

If you don't want to deploy your application in every test, you can add a module-scoped `app` fixture that deploys your charm and waits for it to go active.

The following fixture assumes that the charm has already been packed with `charmcraft pack` -- for example, in a previous CI step:

```python
# tests/integration/conftest.py

import pathlib

import jubilant
import pytest

@pytest.fixture(scope='module')
def app(juju: jubilant.Juju):
    juju.deploy(
        charm_path('mycharm'),
        'mycharm',
        resources={
            'mycharm-image': 'ghcr.io/canonical/...',
        },
        config={
            'base_url': '/api',
            'port': 80,
        },
        base='ubuntu@20.04',
    )
    # ... do any other application setup here ...
    juju.wait(jubilant.all_active)

    yield 'mycharm'  # run the test


def charm_path(name: str) -> pathlib.Path:
    """Return full absolute path to given test charm."""
    # We're in tests/integration/conftest.py, so parent*3 is repo top level.
    charm_dir = pathlib.Path(__file__).parent.parent.parent
    charms = [p.absolute() for p in charm_dir.glob(f'{name}_*.charm')]
    assert charms, f'{name}_*.charm not found'
    assert len(charms) == 1, 'more than one .charm file, unsure which to use'
    return charms[0]
```

In your tests, you'll need to specify that the test depends on both fixtures:

```python
# tests/integration/test_charm.py

def test_active(juju: jubilant.Juju, app: str):
    status = juju.status()
    assert status.apps[app].is_active
```


## Updating the tests themselves

Many features of pytest-operator and python-libjuju map quite directly to Jubilant, except without using `async`. For example, to deploy using

Some are simpler, for example 

TODO
