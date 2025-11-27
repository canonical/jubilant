import json

import pytest

import jubilant

from . import mocks


def test_simple(run: mocks.Run):
    version_dict = {
        'version': '3.6.11-genericlinux-amd64',
        'git-commit': '17876b918429f0063380cdf07dc47f98a890778b',
    }
    run.handle(['juju', 'version', '--format', 'json', '--all'], stdout=json.dumps(version_dict))

    juju = jubilant.Juju()
    version = juju.version()

    assert version == jubilant.Version(
        3,
        6,
        11,
        release='genericlinux',
        arch='amd64',
        git_commit='17876b918429f0063380cdf07dc47f98a890778b',
    )
    assert version.tuple == (3, 6, 11)


@pytest.mark.parametrize(
    'version,expected',
    [
        (
            '3.6.11-genericlinux-amd64',
            jubilant.Version(3, 6, 11, release='genericlinux', arch='amd64'),
        ),
        (
            '4.0.0-genericlinux-amd64',
            jubilant.Version(4, 0, 0, release='genericlinux', arch='amd64'),
        ),
        ('2.3.4-rel-arch', jubilant.Version(2, 3, 4, release='rel', arch='arch')),
        ('3.4.5.6-rel-arch', jubilant.Version(3, 4, 5, build=6, release='rel', arch='arch')),
        ('4.5-beta6-rel-arch', jubilant.Version(4, 5, 6, tag='beta', release='rel', arch='arch')),
        (
            '5.6-alpha7.8-rel-arch',
            jubilant.Version(5, 6, 7, tag='alpha', build=8, release='rel', arch='arch'),
        ),
    ],
)
def test_parsing(version: str, expected: jubilant.Version, run: mocks.Run):
    run.handle(
        ['juju', 'version', '--format', 'json', '--all'], stdout=json.dumps({'version': version})
    )

    juju = jubilant.Juju()
    result = juju.version()

    assert result == expected
    assert str(result) == version


def test_parse_error(run: mocks.Run):
    run.handle(
        ['juju', 'version', '--format', 'json', '--all'], stdout=json.dumps({'version': 'badver'})
    )
    juju = jubilant.Juju()

    with pytest.raises(ValueError):
        juju.version()
