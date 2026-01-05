import jubilant
from tests.unit import mocks

CONSTRAINTS = '{"arch":"amd64","cores":8,"mem":16384}'


def test_get(run: mocks.Run):
    run.handle(['juju', 'model-constraints', '--format', 'json'], stdout=CONSTRAINTS)

    juju = jubilant.Juju()
    values = juju.model_constraints()
    assert values == {'arch': 'amd64', 'cores': 8, 'mem': 16384}


def test_set(run: mocks.Run):
    run.handle(['juju', 'set-model-constraints', 'arch=amd64', 'cores=8', 'mem=16384'])

    juju = jubilant.Juju()
    values = juju.model_constraints(constraints={'arch': 'amd64', 'cores': '8', 'mem': '16384'})
    assert values is None
