import json

from test_status import MINIMAL_JSON, SNAPPASS_JSON

import jubilant


def test_status_str_minimal():
    status = jubilant.Status._from_dict(json.loads(MINIMAL_JSON))
    expected = [
        'Model  Controller  Cloud/Region  Version  Timestamp  Notes',
        'mdl    ctl         aws           3.0.0                    ',
    ]
    assert str(status).splitlines() == expected


def test_status_str_snappass():
    status = jubilant.Status._from_dict(json.loads(SNAPPASS_JSON))
    expected = [
        'Model  Controller          Cloud/Region        Version  Timestamp       Notes',
        'tt     microk8s-localhost  microk8s/localhost  3.6.1    12:04:55+13:00       ',
        '',
        'App            Version  Status  Scale  Charm          Channel        Rev  Address         Exposed  Message         ',
        'snappass-test           active  1      snappass-test  latest/stable  9    10.152.183.248  no       snappass started',
        '',
        'Unit              Workload  Agent  Machine  Address       Ports  Message',
        'snappass-test/0*  active    idle            10.1.164.138                ',
    ]
    assert str(status).splitlines() == expected
