from __future__ import annotations

import dataclasses
import re
from typing import Any

# Per https://github.com/juju/juju/blob/afed87bbe98189805bc81e1af5d5fac70195fc86/core/semversion/version.go#L86-L91,
# support version strings in the following formats:
#
# 1.2-release-arch
# 1.2.3-release-arch
# 1.2.3.4-release-arch
# 1.2-alpha3-release-arch
# 1.2-alpha3.4-release-arch
majmin = r'^(\d+)\.(\d+)'
relarch = r'([^-]+)-([^-]+)$'
majmin_re = re.compile(rf'{majmin}-{relarch}')
majmin_patch_re = re.compile(rf'{majmin}\.(\d+)-{relarch}')
majmin_patch_build_re = re.compile(rf'{majmin}\.(\d+)\.(\d+)-{relarch}')
majmin_tag_re = re.compile(rf'{majmin}-([a-z]+)(\d+)-{relarch}')
majmin_tag_build_re = re.compile(rf'{majmin}-([a-z]+)(\d+)\.(\d+)-{relarch}')


@dataclasses.dataclass(frozen=True)
class Version:
    """Parsed Juju CLI version as returned by ``juju version --format=json --all``.

    The version from Juju is normally in the form ``major.minor.patch-release-arch``.
    You can compare versions using the :attr:`tuple` property::

        if juju.version().tuple >= (3, 6, 11):
            ...  # Juju CLI is at least 3.6.11
    """

    major: int
    minor: int
    patch: int
    release: str = ''
    arch: str = ''

    tag: str | None = None
    build: int | None = None

    git_commit: str | None = None

    def __str__(self) -> str:
        """The string representation of the parsed version.

        This recreates the version string from Juju.
        """
        prefix = f'{self.major}.{self.minor}'
        if self.tag is not None:
            prefix += f'-{self.tag}{self.patch}'
        elif self.patch != 0:
            prefix += f'.{self.patch}'
        if self.build is not None:
            prefix += f'.{self.build}'
        return f'{prefix}-{self.release}-{self.arch}'

    @property
    def tuple(self) -> tuple[int, int, int]:
        """The tuple ``(major, minor, patch)``."""
        return self.major, self.minor, self.patch

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> Version:
        version = d['version']
        patch = 0
        tag = None
        build = None

        if match := majmin_re.match(version):
            major, minor, release, arch = match.groups()
        elif match := majmin_patch_re.match(version):
            major, minor, patch, release, arch = match.groups()
        elif match := majmin_patch_build_re.match(version):
            major, minor, patch, build, release, arch = match.groups()
        elif match := majmin_tag_re.match(version):
            major, minor, tag, patch, release, arch = match.groups()
        elif match := majmin_tag_build_re.match(version):
            major, minor, tag, patch, build, release, arch = match.groups()
        else:
            raise ValueError(f'invalid version {version!r}')

        return Version(
            major=int(major),
            minor=int(minor),
            patch=int(patch),
            release=release,
            arch=arch,
            tag=tag,
            build=int(build) if build is not None else None,
            git_commit=d.get('git-commit'),
        )
