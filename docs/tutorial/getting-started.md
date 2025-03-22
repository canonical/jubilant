# Getting started with Jubilant

In this tutorial, we will learn how to install Jubilant, run Juju commands with it, and write a basic charm integration test.

The tutorial assumes that you have a basic understanding of Juju and have already installed it. [Learn how to install the Juju CLI.](https://canonical-juju.readthedocs-hosted.com/en/latest/user/howto/manage-juju/#install-juju)


## Install Jubilant

Jubilant is published to PyPI, so you can install and use it with your favourite Python package manager:

```
$ pip install jubilant
# or
$ uv add jubilant
```


## Ensure it's working

To ensure Jubilant is working, use it to add a Juju model and check Juju's status:

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
    model_status=StatusInfo(current='available', since='22 Mar 2025 12:34:12+13:00'),
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

You can even try deploying a simple charm and waiting till it's ready:

```
$ uv run python
>>> import jubilant
>>> juju = jubilant.Juju(model='test')
>>> juju.deploy('snappass-test')
>>> juju.wait(jubilant.all_active)  # Takes about a minute
Status(
  ...
)
```


## Write a charm integration test

We recommend using [pytest](https://docs.pytest.org/en/stable/) for writing tests. Here is a test that deploys a charm and waits for it to be active:

```python
def test_deploy():
    juju = jubilant.Juju()
    juju.add_model('test')  # See below for a fixture to do this
    try:
        juju.deploy('snappass-test')
        juju.wait(jubilant.all_active)
    finally:
        juju.destroy_model('test')
```

We also recommend using [concierge](https://github.com/jnsgruk/concierge/) to set up Juju in CI. It will install Juju with a provider like Microk8s and bootstrap a controller for you. For example, using GitHub Actions:

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
  run: uv run pytest tests/integration -vv --log-level=INFO
```


## Write a model-setup fixture

You can use a [pytest fixture](https://docs.pytest.org/en/stable/explanation/fixtures.html) to create a temporary model for your test. The [](jubilant.temp_model) context manager helps with this: it creates a randomly-named model on entry, and destroys the model on exit.

A simple model-setup fixture can be written as follows, normally defined in [`conftest.py`](https://docs.pytest.org/en/stable/reference/fixtures.html#conftest-py-sharing-fixtures-across-multiple-files):

```python
@pytest.fixture
def juju():
    with jubilant.temp_model() as juju:
        yield juju
```

Using the fixture, the integration test we saw earlier becomes even simpler:

```python
def test_deploy(juju: jubilant.Juju):
    juju.deploy('snappass-test')
    juju.wait(jubilant.all_active)
```

You may want to make the fixture ["module-scoped"](https://docs.pytest.org/en/stable/how-to/fixtures.html#scope-sharing-fixtures-across-classes-modules-packages-or-session), to allow all the tests in one file to share the same temporary model. To do this, add a scope to the `pytest.fixture` line:

```
@pytest.fixture(scope='module')
```

See [Jubilant's own `conftest.py`](https://github.com/canonical/jubilant/blob/main/tests/integration/conftest.py) for examples of how to:

- Add a `--keep-models` command-line argument to keep the models after running each test
- Print the `juju debug-log` on test failure


## Use a custom `wait` condition

When waiting on a condition with [`Juju.wait`](jubilant.Juju.wait), you can use pre-defined helpers like [](jubilant.all_active) or [](jubilant.any_error), but you can also define a custom condition using the *ready* or *error* parameters. This is typically done with inline `lambda` functions.

For example, to test that the `myapp` charm starts up with application status "unknown":

```
def test_unknown(juju: jubilant.Juju):
    juju.deploy('myapp')
    juju.wait(
    	lambda status: status.apps['myapp'].app_status.current == 'unknown',
    )
```

There are also `is_*` properties on the `AppStatus` and `UnitStatus` classes for the common statuses: `is_active`, `is_blocked`, `is_error`, `is_maintenance`, and `is_waiting`.

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

Many common Juju commands are already on the `Juju` class, such as [`deploy`](jubilant.Juju.deploy), [`integrate`](jubilant.Juju.deploy), and so on.

However, if you want to run a Juju command that's not (yet) built in to Jubilant, you can fall back to calling the [`Juju.cli`](jubilant.Juju.cli) method. For example, to fetch a model configuration value using `juju model-config`:

```python
>>> import json
>>> import jubilant
>>> juju = jubilant.Juju(model='test')
>>> stdout = juju.cli('model-config', '--format', 'json')
>>> result = json.loads(stdout)
>>> result['automatically-retry-hooks']
{'Value': True, 'Source': 'default'}
```

By default, `Juju.cli` adds the `--model=<model>` parameter if the `Juju` instance has a model set. To prevent this for commands not specific to a model, specify `include_model=False`:

```python
>>> stdout = juju.cli('controllers', '--format', 'json', include_model=False)
>>> result = json.loads(stdout)
>>> result['controllers']['k8s']['uuid']
'cda7763e-05fc-4e55-80ab-7b39badaa50d'
```

(next_steps)=
## Next steps

You've now learned all the basics of Jubilant! For more information, look over [the API reference](/reference/jubilant).

If you have any problems or want to request new features, please [open an issue](https://github.com/canonical/jubilant/issues/new).
