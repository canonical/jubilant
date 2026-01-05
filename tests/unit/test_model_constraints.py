import pytest

import jubilant
from tests.unit import mocks


def test_get(run: mocks.Run):
    run.handle(
        ['juju', 'model-constraints', '--format', 'json'],
        stdout='{"arch":"amd64","cores":8,"mem":16384}',
    )

    juju = jubilant.Juju()
    values = juju.model_constraints()
    assert values == {'arch': 'amd64', 'cores': 8, 'mem': 16384}


def test_set(run: mocks.Run):
    run.handle(
        [
            'juju',
            'set-model-constraints',
            'arch=amd64',
            'cores=8',
            'mem=16384',
            'allocate-public-ip=false',
        ]
    )

    juju = jubilant.Juju()
    retval = juju.model_constraints(
        {'arch': 'amd64', 'cores': 8, 'mem': '16384', 'allocate-public-ip': False}
    )
    assert retval is None


def test_format_constraint_type_error():
    juju = jubilant.Juju()
    with pytest.raises(TypeError):
        juju.model_constraints({'foo': None})  # type: ignore
