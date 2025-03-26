# Getting started with Jubilant

In this tutorial, we'll learn how to install Jubilant, use it to run Juju commands, and write a simple charm integration test.

The tutorial assumes that you have a basic understanding of Juju and have already installed it. [Learn how to install the Juju CLI.](https://canonical-juju.readthedocs-hosted.com/en/latest/user/howto/manage-juju/#install-juju)


## Install Jubilant

Jubilant is published to PyPI, so you can install and use it with your favorite Python package manager:

```
$ pip install jubilant
# or
$ uv add jubilant
```

Jubilant requires Python 3.12 or above. If your charm uses an Ubuntu base with an older Python version, run your integration tests with Python 3.12+ and install Jubilant with the requirement `jubilant;python_version>='3.12'` ([see an example](https://github.com/jnsgruk/zinc-k8s-operator/pull/355/files)).


## Check your setup

To check that Jubilant is working, use it to add a Juju model and check its status:

```
$ uv run python
>>> import jubilant
>>> juju = jubilant.Juju()
>>> juju.add_model('test')
>>> juju.status()
Status(
  model=ModelStatus(
    name='test',
    type='caas',
    controller='k8s',
    cloud='my-k8s',
    version='3.6.4',
    region='localhost',
    model_status=StatusInfo(
      current='available',
      since='22 Mar 2025 12:34:12+13:00',
    ),
  ),
  machines={},
  apps={},
  controller=ControllerStatus(timestamp='12:34:17+13:00'),
)
```

Compare the status to what's displayed when using the Juju CLI directly:

```
$ juju status --model test
Model  Controller  Cloud/Region      Version  SLA          Timestamp
test   k8s         my-k8s/localhost  3.6.4    unsupported  12:35:05+13:00

Model "test" is empty.
```


## Write a charm integration test

We recommend using [pytest](https://docs.pytest.org/en/stable/) for writing tests. You can define a [pytest fixture](https://docs.pytest.org/en/stable/explanation/fixtures.html) to create a temporary Juju model for each test. The [](jubilant.temp_model) context manager creates a randomly-named model on entry, and destroys the model on exit.

Here is a module-scoped fixture called `juju`, which you would normally define in [`conftest.py`](https://docs.pytest.org/en/stable/reference/fixtures.html#conftest-py-sharing-fixtures-across-multiple-files):

```python
@pytest.fixture(scope='module')
def juju():
    with jubilant.temp_model() as juju:
        yield juju
```

Integration tests in a test file would use the fixture, operating on the temporary model:

```python
def test_deploy(juju: jubilant.Juju):
    juju.deploy('snappass-test')
    status = juju.wait(jubilant.all_active)
    assert status.apps['snappass-test'].scale == 1
```

You may want to adjust the [scope](https://docs.pytest.org/en/stable/how-to/fixtures.html#fixture-scopes) of your `juju` fixture. For example, to create a new model for every test function (pytest's default behavior), omit the scope:

```python
@pytest.fixture
def juju():
    ...
```


## Use a custom `wait` condition

When waiting on a condition with [`Juju.wait`](jubilant.Juju.wait), you can use pre-defined helpers including [](jubilant.all_active) and [](jubilant.any_error). You can also define custom conditions for the *ready* and *error* parameters. This is typically done with inline `lambda` functions.

For example, to test that the `myapp` charm starts up with application status "unknown":

```
def test_unknown(juju: jubilant.Juju):
    juju.deploy('myapp')
    juju.wait(
        lambda status: status.apps['myapp'].app_status.current == 'unknown',
    )
```

There are also `is_*` properties on the [`AppStatus`](jubilant.statustypes.AppStatus) and [`UnitStatus`](jubilant.statustypes.UnitStatus) classes for the common statuses: `is_active`, `is_blocked`, `is_error`, `is_maintenance`, and `is_waiting`.

For example, to wait till `myapp` is active and `yourapp` is blocked, and to raise an error if any app or unit goes into error state:

```
def test_custom_wait(juju: jubilant.Juju):
    juju.deploy('myapp')
    juju.deploy('yourapp')
    juju.wait(
        lambda status: (
            status.apps['myapp'].is_active and
            status.apps['yourapp'].is_blocked
        ),
        error=jubilant.any_error,
    )
```


## Fall back to `Juju.cli` if needed

Many common Juju commands are already defined on the `Juju` class, such as [`deploy`](jubilant.Juju.deploy) and [`integrate`](jubilant.Juju.deploy).

However, if you want to run a Juju command that's not yet defined in Jubilant, you can fall back to calling the [`Juju.cli`](jubilant.Juju.cli) method. For example, to fetch a model configuration value using `juju model-config`:

```python
>>> import json
>>> import jubilant
>>> juju = jubilant.Juju(model='test')
>>> stdout = juju.cli('model-config', '--format=json')
>>> result = json.loads(stdout)
>>> result['automatically-retry-hooks']['Value']
True
```

By default, `Juju.cli` adds a `--model=<model>` parameter if the `Juju` instance has a model set. To prevent this for commands not specific to a model, specify `include_model=False`:

```python
>>> stdout = juju.cli('controllers', '--format=json', include_model=False)
>>> result = json.loads(stdout)
>>> result['controllers']['k8s']['uuid']
'cda7763e-05fc-4e55-80ab-7b39badaa50d'
```


## Use `concierge` in CI

We recommend using [concierge](https://github.com/jnsgruk/concierge/) to set up Juju when running your integration tests in CI. It will install Juju with a provider like MicroK8s and bootstrap a controller for you. For example, using GitHub Actions:

```
- name: Install concierge
  run: sudo snap install --classic concierge

- name: Install Juju and bootstrap
  run: |
      sudo concierge prepare \
          --juju-channel=3/stable \
          --charmcraft-channel=3.x/stable \
          --preset microk8s

- name: Run integration tests
  run: |
      charmcraft pack
      uv run pytest tests/integration -vv --log-level=INFO
```


(next_steps)=
## Next steps

You've now learned the basics of Jubilant! To learn more:

- Look over the [`jubilant` API reference](/reference/jubilant)
- See [Jubilant's own integration tests](https://github.com/canonical/jubilant/blob/main/tests/integration/test_basic.py) for more examples of using `Juju` methods
- See [Jubilant's `conftest.py`](https://github.com/canonical/jubilant/blob/main/tests/integration/conftest.py) with a `juju` fixture that has a `--keep-models` command-line argument, and prints the `juju debug-log` on test failure

If you have any problems or want to request new features, please [open an issue](https://github.com/canonical/jubilant/issues/new).
