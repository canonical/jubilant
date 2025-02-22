import mocks

import jubilant


def test_minimal(run: mocks.Run):
    stdout = """{
        "model": {
            "name": "mdl",
            "type": "typ",
            "controller": "ctl",
            "cloud": "aws",
            "version": "3.0.0"
        },
        "machines": {},
        "applications": {}
    }"""
    run.handle(['juju', 'status', '--format', 'json'], stdout=stdout)
    juju = jubilant.Juju()

    status = juju.status()

    assert status == jubilant.Status(
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


def test_realistic():
    # TODO: get some JSON from a real Juju
    pass
