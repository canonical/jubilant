# Jubilant-backports, the joyful library for integration-testing charms in Juju 2.9 and above

[Jubilant](https://canonical-jubilant.readthedocs-hosted.com) is a Python library that wraps the [Juju](https://juju.is/) CLI for use in charm integration tests. It provides methods that map 1:1 to Juju CLI commands, but with a type-annotated, Pythonic interface.

Jubilant-backports is a Python library that modifies Jubilant to provide support for running with Juju 2.9. It is a drop-in replacement for Jubilant, using the regular Jubilant package code for Juju 3.0 and above, as well as when there are no differences between 2.9 and higher, and custom code from a Jubilant branch otherwise. It supports the Jubilant 1.4 feature set, and future improvements to Jubilant are unlikely to be backported to Jubilant-backports (but security fixes and bug fixes, where required, will be backported).

You should consider using Jubilant-backports if you need to run the same charm integration test suite against Juju 2.9 as well as more modern Juju version.

## Using Jubilant-backports

Jubilant-backports is published to PyPI, so you can install and use it with your favorite Python package manager:

```
$ pip install jubilant-backports
# or
$ uv add jubilant-backports
```

Because Jubilant-backports calls the Juju CLI, you'll also need to [install Juju](https://documentation.ubuntu.com/juju/2.9/howto/manage-juju/index.html#install-juju).

To use Jubilant-backports in Python code:

```python
import jubilant_backports as jubilant

juju = jubilant.Juju()
juju.deploy('snappass-test')
juju.wait(jubilant.all_active)

# Or only wait for specific applications:
juju.wait(lambda status: jubilant.all_active(status, 'snappass-test', 'another-app'))
```

Note that we have done `import jubilant_backports as jubilant` and then used `jubilant.Juju()` rather than `import jubilant_backports` and `jubilant_backports.Juju()`. This will result in a simpler and cleaner change when you are ready to drop support for Juju 2.9, and want to move to the regular Jubilant package: all you need to do is change the dependency and the import statements, and the rest of your tests can be left unchanged.

Below is an example of a charm integration test. First we define a module-scoped [pytest fixture](https://docs.pytest.org/en/stable/explanation/fixtures.html) named `juju` which creates a temporary model and runs the test with a `Juju` instance pointing at that model. Jubilant-backports's `temp_model` context manager creates the model during test setup and destroys it during teardown:

```python
# conftest.py
@pytest.fixture(scope='module')
def juju():
    with jubilant.temp_model() as juju:
        yield juju


# test_deploy.py
def test_deploy(juju: jubilant.Juju):        # Use the "juju" fixture  # type: ignore
    juju.deploy('snappass-test')             # Deploy the charm
    status = juju.wait(jubilant.all_active)  # Wait till the app and unit are 'active'

    # Hit the Snappass HTTP endpoint to ensure it's up and running.
    address = status.apps['snappass-test'].units['snappass-test/0'].address
    response = requests.get(f'http://{address}:5000/', timeout=10)
    response.raise_for_status()
    assert 'snappass' in response.text.lower()
```

You don't have to use pytest with Jubilant-backports, but it's what we recommend. Pytest's `assert`-based approach is a straight-forward way to write tests, and its fixtures are helpful for structuring setup and teardown.


## Contributing and developing

Anyone can contribute to Jubilant-backports. The code lives in a [branch](https://github.com/canonical/jubilant/tree/jubilant-backports) of the regular [Jubilant](https://github.com/canonical/jubilant). It's best to start by [opening an issue](https://github.com/canonical/jubilant/issues) with a clear description of the problem or feature request, but you can also [open a pull request](https://github.com/canonical/jubilant/pulls) directly.

Jubilant-backports uses [`uv`](https://docs.astral.sh/uv/) to manage Python dependencies and tools, so you'll need to [install uv](https://docs.astral.sh/uv/#installation) to work on the library. You'll also need `make` to run local development tasks (but you probably have `make` installed already).

After that, clone the Jubilant codebase, check out the `jubilant-backports` branch, and use `make all` to run various checks and the unit tests:

```
$ git clone https://github.com/canonical/jubilant
Cloning into 'jubilant-backports'...
...
$ cd jubilant-backports
$ git checkout jubilant-backports
$ make all
...
========== 93 passed in 0.81s ==========
```

To contribute a code change, write your fix or feature, add tests and docs, then run `make all` before you push and create a PR. Once you create a PR, GitHub will also run the integration tests, which takes several minutes.

## Doing a release

To create a new release of Jubilant-backports:

1. Update the `__version__` field in [`jubilant_backports/__init__.py`](https://github.com/canonical/jubilant/blob/main/jubilant_backports/__init__.py) to the new version you want to release.
2. Push up a PR with this change and get it reviewed and merged.
3. Create a [new release](https://github.com/canonical/jubilant/releases/new) on GitHub with good release notes. The tag should start with a `backports-v`, like `backports-v1.4.3`. Once you've created the release, the [`publish.yaml` workflow](https://github.com/canonical/jubilant/blob/main/.github/workflows/publish.yaml) will automatically publish it to PyPI.
4. Once the publish workflow has finished, check that the new version appears in the [PyPI version history](https://pypi.org/project/jubilant-backports/#history).
