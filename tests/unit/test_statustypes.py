import json

import jubilant

from .fake_statuses import STATUS_ERRORS_JSON, SUBORDINATES_JSON


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


def test_get_units():
    status = jubilant.Status._from_dict(json.loads(SUBORDINATES_JSON))

    assert sorted(status.get_units('ubuntu')) == ['ubuntu/1']
    assert status.get_units('ubuntu') == status.apps['ubuntu'].units

    assert sorted(status.get_units('ubun2')) == ['ubun2/0']
    assert status.get_units('ubun2') == status.apps['ubun2'].units

    assert sorted(status.get_units('nrpe')) == ['nrpe/1', 'nrpe/2']
    units = status.get_units('nrpe')
    assert units['nrpe/1'].public_address == '10.103.56.99'
    assert units['nrpe/2'].public_address == '10.103.56.129'

    assert status.get_units('foo') == {}
