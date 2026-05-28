# Jubilant, the joyful library for driving Juju

Jubilant is a Python library that wraps the [Juju](https://canonical.com/juju) CLI, primarily for use in charm integration tests. It provides methods that map 1:1 to Juju CLI commands, but with a type-annotated, Pythonic interface.

You should consider switching to Jubilant if your integration tests currently use [pytest-operator](https://github.com/charmed-kubernetes/pytest-operator) (and they probably do). Jubilant has an API you'll pick up quickly, and it avoids some of the pain points of [python-libjuju](https://github.com/juju/python-libjuju/), such as websocket failures and having to use `async`. Read our [design goals](https://documentation.ubuntu.com/jubilant/explanation/design-goals).

Jubilant 1.0.0 was released in April 2025. We'll avoid making breaking changes to the API after this point.

[**Read the full documentation**](https://documentation.ubuntu.com/jubilant/)


## Using Jubilant

Jubilant is published to PyPI, so you can install and use it with your favorite Python package manager:

```
$ pip install jubilant
# or
$ uv add jubilant
```

Because Jubilant calls the Juju CLI, you'll also need to [install Juju](https://documentation.ubuntu.com/juju/3.6/howto/manage-juju/index.html#install-juju).

To use Jubilant in Python code:

```python
import jubilant

juju = jubilant.Juju()
juju.deploy('snappass-test')
juju.wait(jubilant.all_active)

# Or only wait for specific applications:
juju.wait(lambda status: jubilant.all_active(status, 'snappass-test', 'another-app'))
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
