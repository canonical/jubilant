import json

import jubilant

STATUS_ERRORS_JSON = """
{
    "model": {
        "name": "tt",
        "type": "caas",
        "controller": "microk8s-localhost",
        "cloud": "microk8s",
        "version": "3.6.1",
        "model-status": {
            "status-error": "model status error!"
        }
    },
    "machines": {
        "machine-failed": {
            "status-error": "machine status error!"
        }
    },
    "applications": {
        "app-failed": {
            "status-error": "app status error!"
        },
        "unit-failed": {
            "charm": "unit-failed",
            "charm-origin": "origin",
            "charm-name": "unit-failed",
            "charm-rev": 0,
            "exposed": false,
            "units": {
                "unit-failed/0": {
                    "status-error": "unit status error!"
                }
            }
        }
    },
    "offers": {
        "offer-failed": {
            "status-error": "offer status error!"
        }
    },
    "application-endpoints": {
        "remote-app-failed": {
            "status-error": "remote app status error!"
        }
    }
}
"""


def test_juju_status_error():
    status = jubilant.Status._from_dict(json.loads(STATUS_ERRORS_JSON))
    assert status.model.model_status == jubilant.statustypes.StatusInfo(
        current='failed',
        message='model status error!',
    )
    assert status.apps['app-failed'] == jubilant.statustypes.AppStatus(
        charm='<failed>',
        charm_origin='<failed>',
        charm_name='<failed>',
        charm_rev=-1,
        exposed=False,
        app_status=jubilant.statustypes.StatusInfo(current='failed', message='app status error!'),
    )
    assert status.apps['unit-failed'].units['unit-failed/0'] == jubilant.statustypes.UnitStatus(
        workload_status=jubilant.statustypes.StatusInfo(
            current='failed', message='unit status error!'
        ),
        juju_status=jubilant.statustypes.StatusInfo(
            current='failed', message='unit status error!'
        ),
    )
    assert status.machines['machine-failed'] == jubilant.statustypes.MachineStatus(
        machine_status=jubilant.statustypes.StatusInfo(
            current='failed', message='machine status error!'
        ),
        juju_status=jubilant.statustypes.StatusInfo(
            current='failed', message='machine status error!'
        ),
    )
    assert status.offers['offer-failed'] == jubilant.statustypes.OfferStatus(
        app='<failed> (offer status error!)',
        endpoints={},
    )
    assert status.app_endpoints['remote-app-failed'] == jubilant.statustypes.RemoteAppStatus(
        url='<failed>',
        app_status=jubilant.statustypes.StatusInfo(
            current='failed', message='remote app status error!'
        ),
    )
