import json

import pytest

import jubilant_backports as jubilant
from jubilant_backports import statustypes

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
            app_status=statustypes.StatusInfo(current='failed', message='app status error!'),
        )
        assert status.machines['machine-failed'] == statustypes.MachineStatus(
            series=None,
            machine_status=statustypes.StatusInfo(
                current='failed', message='machine status error!'
            ),
            juju_status=statustypes.StatusInfo(current='failed', message='machine status error!'),
        )
    else:
        status = jubilant.Status._from_dict(json.loads(input_status))
        assert status.apps['app-failed'] == statustypes.AppStatus(
            charm='<failed>',
            charm_origin='<failed>',
            charm_name='<failed>',
            charm_rev=-1,
            exposed=False,
            app_status=statustypes.StatusInfo(current='failed', message='app status error!'),
        )
        assert status.machines['machine-failed'] == statustypes.MachineStatus(
            machine_status=statustypes.StatusInfo(
                current='failed', message='machine status error!'
            ),
            juju_status=statustypes.StatusInfo(current='failed', message='machine status error!'),
        )
    assert status.model.model_status == statustypes.StatusInfo(
        current='failed',
        message='model status error!',
    )
    assert status.apps['unit-failed'].units['unit-failed/0'] == statustypes.UnitStatus(
        workload_status=statustypes.StatusInfo(current='failed', message='unit status error!'),
        juju_status=statustypes.StatusInfo(current='failed', message='unit status error!'),
    )
    assert status.offers['offer-failed'] == statustypes.OfferStatus(
        app='<failed> (offer status error!)',
        endpoints={},
    )
    assert status.app_endpoints['remote-app-failed'] == statustypes.RemoteAppStatus(
        url='<failed>',
        app_status=statustypes.StatusInfo(current='failed', message='remote app status error!'),
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
    status = jubilant.Status._from_dict(json.loads(input_status))

    assert sorted(status.get_units('ubuntu')) == [ubuntu_unit]
    assert status.get_units('ubuntu') == status.apps['ubuntu'].units

    assert sorted(status.get_units('ubun2')) == [ubun2_unit]
    assert status.get_units('ubun2') == status.apps['ubun2'].units

    assert sorted(status.get_units('nrpe')) == [nrpe1, nrpe2]
    units = status.get_units('nrpe')
    assert units[nrpe1].public_address == addr1
    assert units[nrpe2].public_address == addr2

    assert status.get_units('foo') == {}
