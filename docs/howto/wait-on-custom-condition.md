---
myst:
  html_meta:
    description: Define custom wait conditions for Juju.wait using lambdas, named functions, and status helpers.
---

(use_a_custom_wait_condition)=
# How to wait on a custom condition

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
