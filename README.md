# Jubilant, the joyful library for integration-testing Juju charms

Jubilant is a Python library that wraps the [Juju](https://juju.is/) CLI for use in charm integration tests. It provides methods that map 1:1 to Juju CLI commands, but with a type-annotated, Pythonic interface.

You should consider switching to Jubilant if your integration tests currently use [pytest-operator](https://github.com/charmed-kubernetes/pytest-operator) (and they probably do). Jubilant has an API you'll pick up quickly, and it avoids some of the pain points of [python-libjuju](https://github.com/juju/python-libjuju/), such as websocket failures and having to use `async`. Read our [design goals](https://canonical-jubilant.readthedocs-hosted.com/explanation/design-goals).

Jubilant requires Python 3.12 or above. If your charm uses an Ubuntu base with an older Python version, run your integration tests with Python 3.12+ and install Jubilant with the requirement `jubilant;python_version>='3.12'` ([see an example](https://github.com/jnsgruk/zinc-k8s-operator/pull/355/files)).

Jubilant is currently in pre-release or "beta" phase (see [PyPI releases](https://pypi.org/project/jubilant/#history)). Our intention is to release version 1.0.0 in May 2025.

[**Read the full documentation**](https://canonical-jubilant.readthedocs-hosted.com/)


## Using Jubilant

Jubilant is published to PyPI, so you can install and use it with your favorite Python package manager:

```
$ pip install jubilant
# or
$ uv add jubilant
```

Because Jubilant calls the Juju CLI, you'll also need to [install Juju](https://canonical-juju.readthedocs-hosted.com/en/latest/user/howto/manage-juju/#install-juju).

To use Jubilant in Python code:

```python
import jubilant

juju = jubilant.Juju()
juju.deploy('snappass-test')
juju.wait(jubilant.all_active)
```

Below is an example of a charm integration test. First we define a module-scoped [pytest fixture](https://docs.pytest.org/en/stable/explanation/fixtures.html) named `juju` which creates a temporary model and runs the test with a `Juju` instance pointing at that model. Jubilant's`temp_model` context manager creates the model during test setup and destroys it during teardown:

```python
# conftest.py
@pytest.fixture(scope='module')
def juju():
    with jubilant.temp_model() as juju:
        yield juju


# test_deploy.py
def test_deploy(juju: jubilant.Juju):        # Use the "juju" fixture
    juju.deploy('snappass-test')             # Deploy the charm
    status = juju.wait(jubilant.all_active)  # Wait till the app and unit are 'active'

    # Hit the Snappass HTTP endpoint to ensure it's up and running.
    address = status.apps['snappass-test'].units['snappass-test/0'].address
    response = requests.get(f'http://{address}:5000/', timeout=10)
    response.raise_for_status()
    assert 'snappass' in response.text.lower()
```

You don't have to use pytest with Jubilant, but it's what we recommend. Pytest's `assert`-based approach is a straight-forward way to write tests, and its fixtures are helpful for structuring setup and teardown.


## Contributing and developing

Anyone can contribute to Jubilant. It's best to start by [opening an issue](https://github.com/canonical/jubilant/issues) with a clear description of the problem or feature request, but you can also [open a pull request](https://github.com/canonical/jubilant/pulls) directly.

Jubilant uses [`uv`](https://docs.astral.sh/uv/) to manage Python dependencies and tools, so you'll need to [install uv](https://docs.astral.sh/uv/#installation) to work on the library. You'll also need `make` to run local development tasks (but you probably have `make` installed already).

After that, clone the Jubilant codebase and use `make all` to run various checks and the unit tests:

```
$ git clone https://github.com/canonical/jubilant
Cloning into 'jubilant'...
...
$ cd jubilant
$ make all
...
========== 107 passed in 0.26s ==========
```

To contribute a code change, write your fix or feature, add tests and docs, then run `make all` before you push and create a PR. Once you create a PR, GitHub will also run the integration tests, which takes several minutes.


## Doing a release

To create a new release of Jubilant:

1. Update the `__version__` field in [`jubilant/__init__.py`](https://github.com/canonical/jubilant/blob/main/jubilant/__init__.py) to the new version you want to release.
2. Push up a PR with this change and get it reviewed and merged.
3. Create a [new release](https://github.com/canonical/jubilant/releases/new) on GitHub with good release notes. The tag should start with a `v`, like `v1.2.3`. Once you've created the release, the [`publish.yaml` workflow](https://github.com/canonical/jubilant/blob/main/.github/workflows/publish.yaml) will automatically publish it to PyPI.
4. Once the publish workflow has finished, check that the new version appears in the [PyPI version history](https://pypi.org/project/jubilant/#history).
