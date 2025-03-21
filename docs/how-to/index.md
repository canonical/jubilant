# How-to guides

These guides walk you through key operations you can perform with Jubilant.


## Define a custom `wait` condition

When waiting on a condition with `Juju.wait`, you can use the existing `jubilant.all_*` and `jubilant.any_*` helpers, but you can also define a custom condition.

```{toctree}
:titlesonly:
:maxdepth: 1

Define a custom wait condition <custom-wait>
```

## Write a model-setup fixture

When using Pytest, you can write small fixtures that set up (and tear down) a temporary model for use in the integration test.

```{toctree}
:titlesonly:
:maxdepth: 1

Write a model-setup fixture <model-fixture>
```
