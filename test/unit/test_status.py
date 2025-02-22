import mocks

import jubilant

MINIMAL_JSON = """
{
    "model": {
        "name": "mdl",
        "type": "typ",
        "controller": "ctl",
        "cloud": "aws",
        "version": "3.0.0"
    },
    "machines": {},
    "applications": {}
}
"""

MINIMAL_STATUS = jubilant.Status(
    model=jubilant.statustypes.ModelStatus(
        name='mdl',
        type='typ',
        controller='ctl',
        cloud='aws',
        version='3.0.0',
    ),
    machines={},
    apps={},
)


def test_minimal_no_model(run: mocks.Run):
    run.handle(['juju', 'status', '--format', 'json'], stdout=MINIMAL_JSON)
    juju = jubilant.Juju()

    status = juju.status()

    assert status == MINIMAL_STATUS


def test_minimal_with_model(run: mocks.Run):
    run.handle(['juju', 'status', '--model', 'mdl', '--format', 'json'], stdout=MINIMAL_JSON)
    juju = jubilant.Juju(model='mdl')

    status = juju.status()

    assert status == MINIMAL_STATUS


def test_realistic():
    # TODO: get some JSON from a real Juju
    pass
