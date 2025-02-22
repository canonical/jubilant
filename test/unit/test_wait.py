import mocks
from test_status import MINIMAL_JSON, MINIMAL_STATUS

import jubilant


def test_wait_defaults(run: mocks.Run, time: mocks.Time):
    run.handle(['juju', 'status', '--format', 'json'], stdout=MINIMAL_JSON)
    juju = jubilant.Juju()

    status = juju.wait(lambda _: True)

    assert run.call_count == 3
    assert time.monotonic() == 2
    assert status == MINIMAL_STATUS


def test_wait_delay_successes(run: mocks.Run, time: mocks.Time):
    run.handle(['juju', 'status', '--format', 'json'], stdout=MINIMAL_JSON)
    juju = jubilant.Juju()

    status = juju.wait(lambda _: True, delay=0.5, successes=5)

    assert run.call_count == 5
    assert time.monotonic() == 2.0
    assert status == MINIMAL_STATUS


# TODO: other wait tests
