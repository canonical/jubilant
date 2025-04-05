import json

import jubilant

from .fake_statuses import DATABASE_WEBAPP_JSON, MINIMAL_STATUS, SNAPPASS_JSON


def test_small():
    status_repr = repr(MINIMAL_STATUS)
    assert (
        status_repr
        == """\
Status(
  model=ModelStatus(name='mdl', type='typ', controller='ctl', cloud='aws', version='3.0.0'),
  machines={},
  apps={},
)"""
    )
    assert str(MINIMAL_STATUS) == status_repr

    # Ensure it's actually a Python repr: it can roundtrip via eval()
    assert eval(status_repr, jubilant.statustypes.__dict__) == MINIMAL_STATUS


def test_medium():
    status = jubilant.Status._from_dict(json.loads(SNAPPASS_JSON))
    status_repr = repr(status)
    assert (
        status_repr
        == """\
Status(
  model=ModelStatus(
    name='tt',
    type='caas',
    controller='microk8s-localhost',
    cloud='microk8s',
    version='3.6.1',
    region='localhost',
    model_status=StatusInfo(current='available', since='24 Feb 2025 12:02:57+13:00'),
  ),
  machines={},
  apps={
    'snappass-test': AppStatus(
      charm='snappass-test',
      charm_origin='charmhub',
      charm_name='snappass-test',
      charm_rev=9,
      exposed=False,
      base=FormattedBase(name='ubuntu', channel='20.04'),
      charm_channel='latest/stable',
      scale=1,
      provider_id='276bec9f-6a0c-46ea-8094-aca6337d46e5',
      address='10.152.183.248',
      app_status=StatusInfo(current='active', message='snappass started', since='24 Feb 2025 12:03:17+13:00'),
      units={
        'snappass-test/0': UnitStatus(
          workload_status=StatusInfo(current='active', message='snappass started', since='24 Feb 2025 12:03:17+13:00'),
          juju_status=StatusInfo(current='idle', since='24 Feb 2025 12:03:18+13:00', version='3.6.1'),
          leader=True,
          address='10.1.164.138',
          provider_id='snappass-test-0',
        ),
      },
    ),
  },
  controller=ControllerStatus(timestamp='12:04:55+13:00'),
)"""
    )
    assert str(status) == status_repr
    assert eval(status_repr, jubilant.statustypes.__dict__) == status


def test_large():
    status = jubilant.Status._from_dict(json.loads(DATABASE_WEBAPP_JSON))
    status_repr = repr(status)
    assert (
        status_repr
        == """\
Status(
  model=ModelStatus(
    name='tt',
    type='caas',
    controller='microk8s-localhost',
    cloud='microk8s',
    version='3.6.1',
    region='localhost',
    model_status=StatusInfo(current='available', since='24 Feb 2025 12:02:57+13:00'),
  ),
  machines={},
  apps={
    'database': AppStatus(
      charm='local:database-0',
      charm_origin='local',
      charm_name='database',
      charm_rev=0,
      exposed=False,
      base=FormattedBase(name='ubuntu', channel='22.04'),
      scale=1,
      provider_id='fa764a56-2b71-4f7e-a6eb-b265f13adc4c',
      address='10.152.183.228',
      app_status=StatusInfo(current='active', message='relation-created: added new secret', since='24 Feb 2025 16:59:43+13:00'),
      relations={
        'db': [
          AppStatusRelation(related_app='webapp', interface='dbi', scope='global'),
          AppStatusRelation(related_app='dummy', interface='xyz', scope='foobar'),
        ],
      },
      units={
        'database/0': UnitStatus(
          workload_status=StatusInfo(current='active', message='relation-created: added new secret', since='24 Feb 2025 16:59:43+13:00'),
          juju_status=StatusInfo(current='idle', since='24 Feb 2025 16:59:44+13:00', version='3.6.1'),
          leader=True,
          open_ports=['8080/tcp'],
          address='10.1.164.190',
          provider_id='database-0',
        ),
      },
      endpoint_bindings={'': 'alpha', 'db': 'alpha'},
    ),
    'webapp': AppStatus(
      charm='local:webapp-0',
      charm_origin='local',
      charm_name='webapp',
      charm_rev=0,
      exposed=False,
      base=FormattedBase(name='ubuntu', channel='22.04'),
      scale=1,
      provider_id='5c49f9f9-09b3-4212-8a36-dfc081ee80b3',
      address='10.152.183.254',
      app_status=StatusInfo(current='active', message="relation-changed: would update web app's db secret", since='24 Feb 2025 16:59:43+13:00'),
      relations={
        'db': [
          AppStatusRelation(related_app='database', interface='dbi', scope='global'),
        ],
      },
      units={
        'webapp/0': UnitStatus(
          workload_status=StatusInfo(current='active', message="relation-changed: would update web app's db secret", since='24 Feb 2025 16:59:43+13:00'),
          juju_status=StatusInfo(current='idle', since='24 Feb 2025 16:59:44+13:00', version='3.6.1'),
          leader=True,
          address='10.1.164.179',
          provider_id='webapp-0',
        ),
      },
      endpoint_bindings={'': 'alpha', 'db': 'alpha'},
    ),
  },
  controller=ControllerStatus(timestamp='17:00:33+13:00'),
)"""
    )
    assert str(status) == status_repr
    assert eval(status_repr, jubilant.statustypes.__dict__) == status


def test_diff():
    # It's simplest to test _status_diff directly, even though it's not public.
    old_json = json.loads(DATABASE_WEBAPP_JSON)
    new_json = json.loads(DATABASE_WEBAPP_JSON)
    new_json['applications']['database']['application-status']['current'] = 'waiting'
    new_json['applications']['database']['application-status']['since'] = (
        '24 Feb 2025 17:59:43+13:00'
    )
    new_json['applications']['database']['relations']['db'][0]['scope'] = 'testy'
    del new_json['applications']['database']['relations']['db'][1]
    old_status = jubilant.Status._from_dict(old_json)
    new_status = jubilant.Status._from_dict(new_json)

    diff = jubilant._juju._status_diff(old_status, new_status)

    assert (
        diff
        == """\
- .apps['database'].app_status.current = 'active'
+ .apps['database'].app_status.current = 'waiting'
- .apps['database'].relations['db'][0].scope = 'global'
- .apps['database'].relations['db'][1].related_app = 'dummy'
- .apps['database'].relations['db'][1].interface = 'xyz'
- .apps['database'].relations['db'][1].scope = 'foobar'
+ .apps['database'].relations['db'][0].scope = 'testy'"""
    )
