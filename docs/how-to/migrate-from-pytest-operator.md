# How to migrate from pytest-operator to Jubilant

Many charm integration tests use [pytest-operator](https://github.com/charmed-kubernetes/pytest-operator) and [python-libjuju](https://github.com/juju/python-libjuju). This guide explains how to migrate your integration tests from those libraries to Jubilant.

To get help while you're migrating tests, please keep the [API reference](/reference/jubilant) handy, and make use of your IDE's autocompletion -- Jubilant tries to provide good type annotations and docstrings.

Migrating your tests can be broken into three steps:

1. Update your dependencies
2. Add fixtures to `conftest.py`
3. Update the tests themselves

Let's look at each of these in turn.


## Update your dependencies

The first thing you'll need to do is add `jubilant` as a dependency to your `tox.ini` or `pyproject.toml` dependencies. Before Jubilant 1.0 is released, you should consider locking it to a specific version.

You can also remove the dependencies on `juju` (python-libjuju), `pytest-operator`, and `pytest-asyncio`.

If using `tox.ini`, the diff might look something like this:

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


## Add fixtures to `conftest.py`

The pytest-operator library includes pytest fixtures, but Jubilant does not include any fixtures, so you'll need to add one or two fixtures to your `conftest.py`.

### A `juju` model fixture

Jubilant expects that a Juju controller has already been set up, either using [Concierge](https://github.com/jnsgruk/concierge) or a manual approach. However, you'll want a fixture to create a temporary model. We recommend naming the fixture `juju`:

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

If you don't want to deploy your application in a test itself, you can add a module-scoped `app` fixture that deploys your charm and waits for it to go active.

The following fixture assumes that the charm has already been packed with `charmcraft pack` in a previous CI step (Jubilant has no equivalent of `ops_test.build_charm`):

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


## Update the tests themselves

Many features of pytest-operator and python-libjuju map quite directly to Jubilant, except without using `async`. Here is a summary of what you need to change:

- Remove `async` and `await` keywords, and replace `pytest_asyncio.fixture` with `pytest.fixture`
- Replace introspection of python-libjuju's `Application` and `Unit` objects with [`juju.status`](jubilant.Juju.status)
- Replace `model.wait_for_idle` with [`juju.wait`](jubilant.Juju.wait) and an appropriate *ready* callable
- Replace `unit.run` with [`juju.exec`](jubilant.Juju.exec); note the different return type and error handling
- Replace `unit.run_action` with [`juju.run`](jubilant.Juju.run); note the different return type and error handling
- Replace other python-libjuju methods with equivalent [`Juju`](jubilant.Juju) methods, which are normally much closer to the Juju CLI commands

Let's look at some specifics in more detail.

### Deploying a charm

To migrate a charm deployment from pytest-operator, drop the `await`, change `series` to `base`, and replace `model.wait_for_idle` with [`juju.wait`](jubilant.Juju.wait):

```python
# pytest-operator
postgres_app = await model.deploy(
    'postgresql-k8s',
    channel='14/stable',
    series='jammy',
    revision=300,
    trust=True,
    config={'profile': 'testing'},
)
await model.wait_for_idle(apps=[postgres_app.name], status='active')

# jubilant
juju.deploy(
    'postgresql-k8s',
    channel='14/stable',
    base='ubuntu@22.04',
    revision=300,
    trust=True,
    config={'profile': 'testing'},
)
juju.wait(lambda status: status.apps['postgresql-k8s'].is_active)
```

### Fetching status

A python-libjuju model is updated in the background using websockets. In Jubilant you use ordinary Python function calls to fetch updates:

```python
# pytest-operator
async def test_active(app: Application):
    assert app.units[0].workload_status == ActiveStatus.name

# jubilant
def test_active(juju: jubilant.Juju, app: str):
    status = juju.status()
    assert status.apps[app].units[app + '/0'].is_active
```

### Waiting for a condition

However, instead of calling `status` directly, it's usually better to wait for a certain condition to be true. In python-libjuju you used `model.wait_for_idle`; in Jubilant you use [`juju.wait`](jubilant.Juju.wait), which has a simpler and more consistent API.

It takes a *ready* callable which takes a [`Status`](jubilant.Status) -- `wait` polls `juju status` every second and calls the ready callable, which must return True three times in a row (configurable).

You can optionally provide an *error* callable, which also takes a `Status`, and if that returns True, `wait` raises a [`WaitError`](jubilant.WaitError) immediately.

Jubilant provides helper functions to use for the *ready* and *error* callables, such as [`jubilant.all_active`](jubilant.all_active) and [`jubilant.any_error`](jubilant.any_error). These check whether the status of all (or any) applications and their units are in a given state.

For example, a simple `wait` call that waits for all applications and units to go "active" and raises an error if any go into "error", would look like this:

```python
# pytest-operator
async def test_active(model: Model):
    await model.deploy('mycharm')
    await model.wait_for_idle(status='active')  # implies raise_on_error=True

# jubilant
def test_active(juju: jubilant.Juju):
    juju.deploy('mycharm')
    juju.wait(jubilant.all_active, error=jubilant.any_error)
```

It's common to use a `lambda` function to customize the callables further. For example, to wait specifically till `mysql` and `redis` are active:

```python
juju.wait(lambda status: jubilant.all_active(status, ['mysql', 'redis']))
```

The `wait` method also has other options (see the [reference docs](jubilant.Juju.wait)):

```python
juju.deploy('mycharm')
juju.wait(
    ready=lambda status: status.apps['mycharm'].is_active,
    error=jubilant.any_error,
    delay=0.2,    # poll "juju status" every 200ms (default 1s)
    timeout=60,   # set overall timeout to 60s (default juju.wait_timeout)
    successes=7,  # require ready to return success 7x in a row (default 3)
)
```


### Integrating two applications

To integrate two charms, remove the `async`-related code and replace `model.add_relation` with [`juju.integrate`](jubilant.Juju.integrate). For example, to integrate discourse-k8s with three other charms:

```python
# pytest-operator
await asyncio.gather(
    model.add_relation('discourse-k8s', 'postgresql-k8s:database'),
    model.add_relation('discourse-k8s', 'redis-k8s'),
    model.add_relation('discourse-k8s', 'nginx-ingress-integrator'),
)
await model.wait_for_idle(status='active')

# jubilant
juju.integrate('discourse-k8s', 'postgresql-k8s:database')
juju.integrate('discourse-k8s', 'redis-k8s')
juju.integrate('discourse-k8s', 'nginx-ingress-integrator')
juju.wait(jubilant.all_active)
```

### Executing a command

In `pytest-operator` tests, you used `unit.run` to execute a command. With Jubilant (like Juju 3.x) you use [`juju.exec`](jubilant.Juju.exec). Jubilant's `exec` returns a [`jubilant.Task`](jubilant.Task), and it also checks errors for you:

```python
# pytest-operator
unit = model.applications['discourse-k8s'].units[0]
action = await unit.run('/bin/bash -c "..."')
await action.wait()
logger.info(action.results)
assert action.results['return-code'] == 0, 'Enable plugins failed'

# jubilant
task = juju.exec('/bin/bash -c "..."', unit='discourse-k8s/0')
logger.info(task.results)
```

### Running an action

In `pytest-operator` tests, you used `unit.run_action` to run an action. With Jubilant, you use [`juju.run`](jubilant.Juju.run). Similar to `exec`, Jubilant's `run` returns a [`jubilant.Task`](jubilant.Task) and checks errors for you:

```python
# pytest-operator
app = model.applications['postgresl-k8s']
action = await app.units[0].run_action('get-password', username='operator')
await action.wait()
password = action.results['password']

# jubilant
task = juju.run('postgresql-k8s/0', 'get-password', {'username': 'operator'})
password = task.results['password']
```

### The `cli` fallback

Similar to how you could call `ops_test.juju`, with Jubilant you can call [`juju.cli`](jubilant.Juju.cli) as a fallback to execute an arbitrary Juju command. Once again, it checks errors for you (and raises [`CLIError`](jubilant.CLIError) if the command's exit code is nonzero):

```python
# pytest-operator
return_code, _, scp_err = await ops_test.juju(
    'scp',
    '--container',
    'postgresql',
    './testing_database/testing_database.sql',
    f'{postgres_app.units[0].name}:.',
)
assert return_code == 0, scp_err

# jubilant
juju.cli(
    'scp',
    '--container',
    'postgresql',
    './testing_database/testing_database.sql',
    'postgresql-k8s/0:.',
)
```


## Further information

- [Jubilant's API reference](jubilant)
- [This discourse-k8s migration PR](https://github.com/canonical/discourse-k8s-operator/pull/326) shows what migrating a real charm's integration tests looks like
