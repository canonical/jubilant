---
myst:
  html_meta:
    description: Run arbitrary Juju CLI commands when they are not yet defined in Jubilant.
---

(fall_back_to_cli)=
# How to run Juju CLI commands

Many common Juju commands are already defined on the `Juju` class, such as [`deploy`](jubilant.Juju.deploy) and [`integrate`](jubilant.Juju.integrate).

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
