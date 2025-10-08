import pytest

import jubilant_backports as jubilant

from .. import mocks


@pytest.mark.parametrize('juju_version', ['2.9.52', '3.6.8'])
def test_wait_timeout(juju_version: str, run: mocks.Run):
    run.handle(
        [
            'juju',
            'exec',
            '--format',
            'json',
            '--unit',
            'ubuntu/0',
            '--timeout' if juju_version[0] == '2' else '--wait',
            '0.001s',
            '--',
            'sleep 1',
        ],
        returncode=1,
        stdout='OUT',
        stderr='... timed out ...',
    )
    juju = jubilant.Juju()
    juju._is_juju_2 = juju_version[0] == '2'

    with pytest.raises(TimeoutError):
        juju.exec('sleep 1', unit='ubuntu/0', wait=0.001)
