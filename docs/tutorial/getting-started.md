# Getting started with Jubilant

In this tutorial, we'll learn how to install Jubilant and use it to run Juju commands.

The tutorial assumes that you have a basic understanding of Juju and have already installed it. {external+juju:ref}`Learn how to install the Juju CLI <install-juju>`.

This tutorial doesn't cover charm integration tests. To learn how to use Jubilant in charm integration tests, see {external+operator:ref}`How to write integration tests for a charm <write-integration-tests-for-a-charm>`.

## Install Jubilant

Jubilant is published to PyPI, so you can install and use it with your favorite Python package manager:

```
$ pip install jubilant
# or
$ uv add jubilant
```

Like the [Ops](https://github.com/canonical/operator) framework used by charms, Jubilant requires Python 3.8 or above.

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
    controller='concierge-k8s',
    cloud='k8s',
    version='3.6.14',
    model_status=StatusInfo(
      current='available',
      since='24 Mar 2026 13:47:11+08:00'
    ),
  ),
  machines={},
  apps={},
  controller=ControllerStatus(
    timestamp='13:47:16+08:00'
  ),
)
```

Compare the status to what's displayed when using the Juju CLI directly:

```
$ juju status --model test
Model  Controller     Cloud/Region  Version  SLA          Timestamp
test   concierge-k8s  k8s           3.6.14   unsupported  13:48:05+08:00

Model "test" is empty.
```

## Deploy a charm

```
$ uv run python
>>> import jubilant
>>> juju = jubilant.Juju(model='test')
>>> juju.deploy('snappass-test')
>>> juju.wait(jubilant.all_active)
>>> # Or wait for just 'snappass-test' to be active (ignoring other apps):
>>> juju.wait(lambda status: jubilant.all_active(status, 'snappass-test'))
Status(
  apps={
    'snappass-test': AppStatus(
      charm='snappass-test',
      charm_origin='charmhub',
      charm_name='snappass-test',
      ...
      units={
        'snappass-test/0': UnitStatus(
          workload_status=StatusInfo(
            current='active',
            message='redis started',
            since='24 Mar 2026 13:50:32+08:00'
          ),
          ...
        ),
      },
    ),
  },
  ...
)
```

This code deploys the `snappass-test` charm from Charmhub.

To deploy a charm from a `.charm` file (created by `charmcraft pack`), use `juju.deploy('/path/to/mycharm.charm')`. For an example, see "Write your tests" in {external+operator:ref}`How to write integration tests for a charm <write-integration-tests-for-a-charm-write-your-tests>`.

(use_a_custom_wait_condition)=
## Use a custom `wait` condition

When waiting on a condition with [`Juju.wait`](jubilant.Juju.wait), you can use pre-defined helpers including [](jubilant.all_active) and [](jubilant.any_error). You can also define custom conditions for the *ready* and *error* parameters. This is typically done with inline `lambda` functions.

For example, to deploy and wait till all the specified applications (`blog`, `mysql`, and `redis`) are "active":

```python
for app in ['blog', 'mysql', 'redis']:
    juju.deploy(app)
juju.integrate('blog', 'mysql')
juju.integrate('blog', 'redis')
juju.wait(
    lambda status: jubilant.all_active(status, 'blog', 'mysql', 'redis'),
)
```

Or to test that the `myapp` charm starts up with application status "unknown":

```python
juju.deploy('myapp')
juju.wait(
    lambda status: status.apps['myapp'].app_status.current == 'unknown',
)
```

There are also `is_*` properties on the [`AppStatus`](jubilant.statustypes.AppStatus) and [`UnitStatus`](jubilant.statustypes.UnitStatus) classes for the common statuses: `is_active`, `is_blocked`, `is_error`, `is_maintenance`, and `is_waiting`. These test the status of a single application or unit, whereas the `jubilant.all_*` and `jubilant.any_*` functions test the statuses of multiple applications *and* all their units.

For larger wait functions, you may want to use a named function with type annotations, so your IDE can provide better autocompletion for `Status` attributes.

For example, to wait till `myapp` is active and `yourapp` is blocked (with "waiting" in the blocked message), and to raise an error if any app or unit goes into error state:

```python
def ready(status: jubilant.Status) -> bool:
    return (
        status.apps['myapp'].is_active and
        status.apps['yourapp'].is_blocked and
        'waiting' in status.apps['yourapp'].app_status.message
    )


juju.deploy('myapp')
juju.deploy('yourapp')
juju.wait(ready, error=jubilant.any_error)
```

You can even ignore the `Status` object and wait for a completely unrelated condition, such as an endpoint on the workload being ready:

```python
juju.deploy('myapp')
juju.wait(lambda _: requests.get('http://workload/status').ok)
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
>>> result['controllers']['concierge-k8s']['uuid']
'cda7763e-05fc-4e55-80ab-7b39badaa50d'
```

(next_steps)=
## Next steps

You've now learned the basics of Jubilant! To learn more:

- Look over the [`jubilant` API reference](/reference/jubilant)
- For examples of using Jubilant in integration tests, see the [httpbin-demo charm's integration tests](https://github.com/canonical/operator/tree/main/examples/httpbin-demo/tests/integration) or [Jubilant's own integration tests](https://github.com/canonical/jubilant/tree/main/tests/integration)

If you have any problems or want to request new features, please [open an issue](https://github.com/canonical/jubilant/issues/new).
