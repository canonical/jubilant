import json

import pytest

import jubilant
import jubilant as real_jubilant

from .fake_statuses import (
    STATUS_ERRORS_JSON,
    STATUS_ERRORS_JSON29,
    SUBORDINATES_JSON,
    SUBORDINATES_JSON29,
)


@pytest.mark.parametrize(
    'version,input_status',
    [
        pytest.param('3.6.8', STATUS_ERRORS_JSON, id='3'),
        pytest.param('2.9.52', STATUS_ERRORS_JSON29, id='2'),
    ],
)
def test_juju_status_error(version: str, input_status: str):
    if version.startswith('2'):
        status = jubilant.Status._from_dict(json.loads(input_status))
        assert status.apps['app-failed'] == jubilant.statustypes.AppStatus(
            charm='<failed>',
            series=None,
            os=None,
            charm_origin='<failed>',
            charm_name='<failed>',
            charm_rev=-1,
            exposed=False,
            app_status=jubilant.statustypes.StatusInfo(
                current='failed', message='app status error!'
            ),
        )
        assert status.machines['machine-failed'] == jubilant.statustypes.MachineStatus(
            series=None,
            machine_status=jubilant.statustypes.StatusInfo(
                current='failed', message='machine status error!'
            ),
            juju_status=jubilant.statustypes.StatusInfo(
                current='failed', message='machine status error!'
            ),
        )
        module = jubilant.statustypes
    else:
        status = real_jubilant.Status._from_dict(json.loads(input_status))
        assert status.apps['app-failed'] == real_jubilant.statustypes.AppStatus(
            charm='<failed>',
            charm_origin='<failed>',
            charm_name='<failed>',
            charm_rev=-1,
            exposed=False,
            app_status=jubilant.statustypes.StatusInfo(
                current='failed', message='app status error!'
            ),
        )
        assert status.machines['machine-failed'] == real_jubilant.statustypes.MachineStatus(
            machine_status=jubilant.statustypes.StatusInfo(
                current='failed', message='machine status error!'
            ),
            juju_status=jubilant.statustypes.StatusInfo(
                current='failed', message='machine status error!'
            ),
        )
        module = real_jubilant.statustypes
    assert status.model.model_status == module.StatusInfo(
        current='failed',
        message='model status error!',
    )
    assert status.apps['unit-failed'].units['unit-failed/0'] == module.UnitStatus(
        workload_status=jubilant.statustypes.StatusInfo(
            current='failed', message='unit status error!'
        ),
        juju_status=jubilant.statustypes.StatusInfo(
            current='failed', message='unit status error!'
        ),
    )
    assert status.offers['offer-failed'] == module.OfferStatus(
        app='<failed> (offer status error!)',
        endpoints={},
    )
    assert status.app_endpoints['remote-app-failed'] == module.RemoteAppStatus(
        url='<failed>',
        app_status=jubilant.statustypes.StatusInfo(
            current='failed', message='remote app status error!'
        ),
    )


@pytest.mark.parametrize(
    'version,input_status,ubuntu_unit,ubun2_unit,addr1,addr2,nrpe1,nrpe2',
    [
        pytest.param(
            '3.6.8',
            SUBORDINATES_JSON,
            'ubuntu/1',
            'ubun2/0',
            '10.103.56.99',
            '10.103.56.129',
            'nrpe/1',
            'nrpe/2',
            id='3',
        ),
        pytest.param(
            '2.9.52',
            SUBORDINATES_JSON29,
            'ubuntu/0',
            'ubun2/0',
            '10.36.4.84',
            '10.36.4.173',
            'nrpe/0',
            'nrpe/1',
            id='2.9',
        ),
    ],
)
def test_get_units(
    version: str,
    input_status: str,
    ubuntu_unit: str,
    ubun2_unit: str,
    addr1: str,
    addr2: str,
    nrpe1: str,
    nrpe2: str,
):
    if version.startswith('2'):
        status = jubilant.Status._from_dict(json.loads(input_status))
    else:
        status = real_jubilant.Status._from_dict(json.loads(input_status))

    assert sorted(status.get_units('ubuntu')) == [ubuntu_unit]
    assert status.get_units('ubuntu') == status.apps['ubuntu'].units

    assert sorted(status.get_units('ubun2')) == [ubun2_unit]
    assert status.get_units('ubun2') == status.apps['ubun2'].units

    assert sorted(status.get_units('nrpe')) == [nrpe1, nrpe2]
    units = status.get_units('nrpe')
    assert units[nrpe1].public_address == addr1
    assert units[nrpe2].public_address == addr2

    assert status.get_units('foo') == {}
