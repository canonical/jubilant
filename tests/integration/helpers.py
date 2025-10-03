from __future__ import annotations

import pathlib

CHARMS_PATH = pathlib.Path(__file__).parent / 'charms'


def find_charm(name: str) -> pathlib.Path:
    """Find given test charm and return absolute path to .charm file."""
    # .charm filename has platform in it, so search with *.charm
    charms = [p.absolute() for p in (CHARMS_PATH / name).glob('*.charm')]
    assert charms, f'{name} .charm file not found'
    assert len(charms) == 1, f'{name} has more than one .charm file, unsure which to use'
    return charms[0]
