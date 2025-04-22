import jubilant

from . import mocks


def test_minimal(run: mocks.Run):
    run.handle(['juju', 'scp', '--', 'SRC', 'DST'])
    juju = jubilant.Juju()

    juju.scp('SRC', 'DST')


def test_all_args(run: mocks.Run):
    run.handle(['juju', 'scp', '--container', 'redis', '--no-host-key-checks', '--', '-r', '-C', 'SRC', 'DST'])
    juju = jubilant.Juju()

    juju.scp('SRC', 'DST', container='redis', host_key_checks=False, scp_options=['-r', '-C'])
