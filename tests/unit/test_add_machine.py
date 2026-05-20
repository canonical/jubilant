import pathlib

import jubilant

from . import mocks


def test_defaults(run: mocks.Run):
    run.handle(['juju', 'add-machine'])
    juju = jubilant.Juju()

    juju.add_machine()


def test_defaults_with_model(run: mocks.Run):
    run.handle(['juju', 'add-machine', '--model', 'mdl'])
    juju = jubilant.Juju(model='mdl')

    juju.add_machine()


def test_to_container(run: mocks.Run):
    run.handle(['juju', 'add-machine', 'lxd:4'])
    juju = jubilant.Juju()

    juju.add_machine('lxd:4')


def test_to_ssh(run: mocks.Run):
    run.handle(['juju', 'add-machine', 'ssh:user@10.10.0.3'])
    juju = jubilant.Juju()

    juju.add_machine('ssh:user@10.10.0.3')


def test_to_provider(run: mocks.Run):
    run.handle(['juju', 'add-machine', 'host.internal'])
    juju = jubilant.Juju()

    juju.add_machine('host.internal')


def test_all_args(run: mocks.Run):
    run.handle(
        [
            'juju',
            'add-machine',
            'ssh:user@10.10.0.3',
            '--base',
            'ubuntu@22.04',
            '--constraints',
            'cores=4',
            '--constraints',
            'mem=16G',
            '--disks',
            'ebs,1T,2 ebs-ssd,100G,1',
            '-n',
            '2',
            '--private-key',
            '/keys/id_ed25519',
            '--public-key',
            '/keys/id_ed25519.pub',
        ]
    )
    juju = jubilant.Juju()

    juju.add_machine(
        'ssh:user@10.10.0.3',
        base='ubuntu@22.04',
        constraints={'cores': 4, 'mem': '16G'},
        disks=['ebs,1T,2', 'ebs-ssd,100G,1'],
        num_machines=2,
        private_key='/keys/id_ed25519',
        public_key='/keys/id_ed25519.pub',
    )


def test_disks_single_str(run: mocks.Run):
    run.handle(['juju', 'add-machine', '--disks', 'ebs,1T,2'])
    juju = jubilant.Juju()

    juju.add_machine(disks='ebs,1T,2')


def test_keys_pathlib(run: mocks.Run):
    run.handle(
        [
            'juju',
            'add-machine',
            'ssh:user@10.10.0.3',
            '--private-key',
            '/keys/id_ed25519',
            '--public-key',
            '/keys/id_ed25519.pub',
        ]
    )
    juju = jubilant.Juju()

    juju.add_machine(
        'ssh:user@10.10.0.3',
        private_key=pathlib.Path('/keys/id_ed25519'),
        public_key=pathlib.Path('/keys/id_ed25519.pub'),
    )
