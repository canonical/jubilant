---
myst:
  html_meta:
    description: Use Juju.wait from the Command-Line Interface.
---

(use_wait_from_cli)=
# How to use `Juju.wait` from CLI

See first: {ref}`use_a_custom_wait_condition`

Jubilant provides an entrypoint to run [`wait`](jubilant.Juju.wait) from the CLI.

```{note}
This is only available from Jubilant v1.13.0 onwards.
```

## Install and run the CLI

If your project defines Jubilant in a dependency group:

```toml
# pyproject.toml
[dependency-groups]
# Dependencies of integration tests
integration = [
    "jubilant>=1.13,<2"
]
```

You can run it from the root of that project with `uv`:

```
uv run --group integration jubilant wait --help
```

You can also run it as a standalone CLI:

```
uvx --from 'jubilant>=1.13.0' jubilant wait --help
```

The rest of this guide will not show the `uv` parts in the sample commands. Please use the suitable one for your setup.

## Ready and error expressions

The `ready` and `--error` CLI arguments are passed as Python expressions, different from how [`Juju.wait`](jubilant.Juju.wait) is used in code. Those expressions have access to three variables: `jubilant` (the [`jubilant`](jubilant) module), `juju` (the [`jubilant.Juju`](jubilant.Juju) instance), and `status` (the [`jubilant.Status`](jubilant.Status) object).

For example, this CLI invocation:

```
jubilant wait 'jubilant.all_active(status, "myapp")' --error 'jubilant.any_error(status)'
```

is equivalent to the following Python call:

```python
juju.wait(
    lambda status: jubilant.all_active(status, 'myapp'),
    error=jubilant.any_error,
)
```

## Setting the Juju binary and model

By default, the CLI uses the `juju` binary on your `PATH` and operates on the current Juju model. To override either of these, use `--juju-cli-bin` and `--model`:

```
jubilant wait 'jubilant.all_active(status)' \
    --juju-cli-bin /snap/bin/juju \
    --model mymodel
```

## Configure logging modes

See first: {external+operator:ref}`Configure Jubilant logs <write-integration-tests-for-a-charm-configure-jubilant-logs>`

By default, `uvx jubilant wait` follows brief logging mode:

```
$ jubilant wait 'jubilant.all_active(status)'

2026-09-08 01:31:43,040 [snappass-test] status: active (snappass started)
2026-09-08 01:31:43,040 [snappass-test/0] status: active (snappass started)
2026-09-08 01:31:45,454 Ready condition succeeded 3 times (jubilant.all_active(status))
```

Use `--quiet` to suppress all output except errors:
```
$ jubilant wait 'jubilant.all_blocked(status)' --timeout 2.0 --quiet

2026-09-08 01:33:47,550 Wait timed out after 2.0 seconds
```

Or `--verbose` to enable verbose logging mode:

```
$ jubilant wait 'jubilant.all_active(status)' --verbose

2026-09-08 01:34:25,406 INFO jubilant.wait [snappass-test] status: active (snappass started)
2026-09-08 01:34:25,406 INFO jubilant.wait [snappass-test/0] status: active (snappass started)
2026-09-08 01:34:25,406 DEBUG jubilant.wait wait: status changed:
+ .model.name = 'mymodel'
+ .model.controller = 'concierge-k8s'
+ .model.cloud = 'k8s'
+ .model.model_status.current = 'available'
+ .apps['snappass-test'].charm = 'snappass-test'
+ .apps['snappass-test'].charm_origin = 'charmhub'
+ .apps['snappass-test'].charm_name = 'snappass-test'
+ .apps['snappass-test'].charm_rev = 9
+ .apps['snappass-test'].exposed = False
+ .apps['snappass-test'].base.name = 'ubuntu'
+ .apps['snappass-test'].base.channel = '20.04'
+ .apps['snappass-test'].charm_channel = 'latest/stable'
+ .apps['snappass-test'].scale = 1
+ .apps['snappass-test'].provider_id = '15a4d580-0623-4d27-ae40-c99527ce5417'
+ .apps['snappass-test'].address = '10.152.183.162'
+ .apps['snappass-test'].app_status.current = 'active'
+ .apps['snappass-test'].app_status.message = 'snappass started'
+ .apps['snappass-test'].units['snappass-test/0'].workload_status.current = 'active'
+ .apps['snappass-test'].units['snappass-test/0'].workload_status.message = 'snappass started'
+ .apps['snappass-test'].units['snappass-test/0'].juju_status.current = 'idle'
+ .apps['snappass-test'].units['snappass-test/0'].juju_status.version = '3.6.28'
+ .apps['snappass-test'].units['snappass-test/0'].leader = True
+ .apps['snappass-test'].units['snappass-test/0'].address = '10.1.0.215'
+ .apps['snappass-test'].units['snappass-test/0'].provider_id = 'snappass-test-0'
2026-09-08 01:34:27,856 INFO jubilant.cli Ready condition succeeded 3 times (jubilant.all_active(status))
```

## Other arguments

The `--delay`, `--timeout`, and `--successes` arguments match the corresponding parameters on [`Juju.wait`](jubilant.Juju.wait). For example:

```
jubilant wait 'jubilant.all_active(status)' \
    --delay 2 \
    --timeout 600 \
    --successes 5
```

is equivalent to the following Python call:

```python
juju.wait(
    lambda status: jubilant.all_active(status),
    delay=2.0,
    timeout=600.0,
    successes=5,
)
```

## Exit codes

| Code | Meaning |
| --- | --- |
| `0` | The `ready` condition succeeded. |
| `1` | The `--error` condition evaluated to true, or an exception was raised while evaluating an expression or waiting. |
| `124` | The wait timed out. |
| `130` | A keyboard interrupt (Ctrl-C) was received while waiting. |
