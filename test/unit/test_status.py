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


SNAPPASS_JSON = """
{
    "model": {
        "name": "tt",
        "type": "caas",
        "controller": "microk8s-localhost",
        "cloud": "microk8s",
        "region": "localhost",
        "version": "3.6.1",
        "model-status": {
            "current": "available",
            "since": "24 Feb 2025 12:02:57+13:00"
        },
        "sla": "unsupported"
    },
    "machines": {},
    "applications": {
        "snappass-test": {
            "charm": "snappass-test",
            "base": {
                "name": "ubuntu",
                "channel": "20.04"
            },
            "charm-origin": "charmhub",
            "charm-name": "snappass-test",
            "charm-rev": 9,
            "charm-channel": "latest/stable",
            "scale": 1,
            "provider-id": "276bec9f-6a0c-46ea-8094-aca6337d46e5",
            "address": "10.152.183.248",
            "exposed": false,
            "application-status": {
                "current": "active",
                "message": "snappass started",
                "since": "24 Feb 2025 12:03:17+13:00"
            },
            "units": {
                "snappass-test/0": {
                    "workload-status": {
                        "current": "active",
                        "message": "snappass started",
                        "since": "24 Feb 2025 12:03:17+13:00"
                    },
                    "juju-status": {
                        "current": "idle",
                        "since": "24 Feb 2025 12:03:18+13:00",
                        "version": "3.6.1"
                    },
                    "leader": true,
                    "address": "10.1.164.138",
                    "provider-id": "snappass-test-0"
                }
            }
        }
    },
    "storage": {},
    "controller": {
        "timestamp": "12:04:55+13:00"
    }
}
"""


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


def test_real_status(run: mocks.Run):
    run.handle(['juju', 'status', '--format', 'json'], stdout=SNAPPASS_JSON)
    juju = jubilant.Juju()

    status = juju.status()

    assert status.model.type == 'caas'
    assert status.apps['snappass-test'].is_active
    assert status.apps['snappass-test'].units['snappass-test/0'].is_active
    assert status.apps['snappass-test'].units['snappass-test/0'].leader
