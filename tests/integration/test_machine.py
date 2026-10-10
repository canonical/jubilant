from __future__ import annotations

import pathlib

import pytest

import jubilant

pytestmark = pytest.mark.machine


@pytest.fixture(scope='module', autouse=True)
def setup(juju: jubilant.Juju, private_key_file: str):
    juju.deploy('ubuntu')
    juju.wait(jubilant.all_active)


def test_exec(juju: jubilant.Juju):
    task = juju.exec('echo foo', machine=0)
    assert task.success
    assert task.return_code == 0
    assert task.stdout == 'foo\n'
    assert task.stderr == ''

    task = juju.exec('echo', 'bar', 'baz', machine=0)
    assert task.success
    assert task.stdout == 'bar baz\n'


def test_ssh(juju: jubilant.Juju, private_key_file: str, ssh_key: str | None):
    # -i is for Juju < 4.1, which connects to the machine directly.
    ssh_options = ['-i', private_key_file]
    output = juju.ssh('ubuntu/0', 'echo', 'UNIT', ssh_options=ssh_options, ssh_key=ssh_key)
    assert output == 'UNIT\n'

    output = juju.ssh(0, 'echo', 'MACHINE', ssh_options=ssh_options, ssh_key=ssh_key)
    assert output == 'MACHINE\n'


def test_add_and_remove_unit(juju: jubilant.Juju):
    juju.add_unit('ubuntu')
    juju.wait(lambda status: jubilant.all_active(status) and len(status.apps['ubuntu'].units) == 2)

    juju.remove_unit('ubuntu/1')
    juju.wait(lambda status: jubilant.all_active(status) and len(status.apps['ubuntu'].units) == 1)


def test_scp_directory(
    juju: jubilant.Juju, private_key_file: str, ssh_key: str | None, tmp_path: pathlib.Path
):
    src_dir = tmp_path / 'src' / 'mydir'
    src_dir.mkdir(parents=True)
    (src_dir / 'a.txt').write_text('A')
    (src_dir / 'b.txt').write_text('B')

    # -i is for Juju < 4.1, which connects to the machine directly.
    scp_options = ['-r', '-i', private_key_file]

    # Local directory to remote
    juju.scp(
        str(src_dir),
        'ubuntu/0:/tmp/mydir',
        scp_options=scp_options,
        ssh_key=ssh_key,
    )

    # Remote directory back to local
    dst_dir = tmp_path / 'dst' / 'mydir'
    dst_dir.parent.mkdir(parents=True)
    juju.scp(
        'ubuntu/0:/tmp/mydir',
        str(dst_dir),
        scp_options=scp_options,
        ssh_key=ssh_key,
    )

    assert (dst_dir / 'a.txt').read_text() == 'A'
    assert (dst_dir / 'b.txt').read_text() == 'B'


def test_model_constraints(juju: jubilant.Juju):
    initial_constraints = juju.model_constraints()
    assert not initial_constraints
    juju.model_constraints(constraints={'mem': '1G', 'cores': 4})
    new_constraints = juju.model_constraints()
    assert new_constraints == {'mem': 1024, 'cores': 4}


def test_add_machine(juju: jubilant.Juju):
    before = set(juju.status().machines)
    juju.add_machine()
    status = juju.wait(lambda s: bool(set(s.machines) - before))
    added = set(status.machines) - before
    assert len(added) == 1
