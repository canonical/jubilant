from __future__ import annotations

import dataclasses
from typing import Any, Literal

from . import _pretty


class TaskError(Exception):
    """Exception raised when an action or exec command fails."""

    task: Task
    """Associated task."""

    def __init__(self, task: Task):
        self.task = task

    def __str__(self) -> str:
        return f'task error: {self.task}'


@dataclasses.dataclass(frozen=True)
class Task:
    """A task holds the results of Juju running an action or exec command on a single unit."""

    id: str
    """Task ID of the action, for use with ``juju show-task``."""

    status: Literal['aborted', 'cancelled', 'completed', 'error', 'failed']
    """Status of the action (Juju operation). Typically "completed" or "failed"."""

    results: dict[str, Any] = dataclasses.field(default_factory=dict)
    """Results of the action provided by the charm.

    This excludes the special "return-code", "stdout", and "stderr" keys
    inserted by Juju; those values are provided by separate attributes.
    """

    return_code: int = 0
    """Return code from executing the charm action hook."""

    stdout: str = ''
    """Stdout printed by the action hook."""

    stderr: str = ''
    """Stderr printed by the action hook."""

    message: str = ''
    """Failure message, if the charm provided a message when it failed the action."""

    log: list[str] = dataclasses.field(default_factory=list)
    """List of messages logged by the action hook."""

    def __str__(self) -> str:
        details: list[str] = []
        if self.results:
            details.append(f'Results: {self.results}')
        if self.stdout:
            details.append(f'Stdout:\n{self.stdout}')
        if self.stderr:
            details.append(f'Stderr:\n{self.stderr}')
        if self.message:
            details.append(f'Message: {self.message}')
        if self.log:
            log_str = '\n'.join(self.log)
            details.append(f'Log:\n{log_str}')
        s = f'Task {self.id}: status {self.status!r}, return code {self.return_code}'
        if details:
            s += ', details:\n' + '\n'.join(details)
        return s

    def __repr__(self) -> str:
        return _pretty.dump(self)

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> Task:
        results: dict[str, Any] = d.get('results') or {}
        return_code = results.pop('return-code', 0)
        stdout = results.pop('stdout', '')
        stderr = results.pop('stderr', '')
        return cls(
            id=d['id'],
            status=d['status'],
            results=results,
            return_code=return_code,
            stdout=stdout,
            stderr=stderr,
            message=d.get('message') or '',
            log=d.get('log') or [],
        )

    @property
    def success(self) -> bool:
        """Whether the action was successful."""
        return self.status == 'completed' and self.return_code == 0

    def raise_on_failure(self):
        """If task was not successful, raise a :class:`TaskError`."""
        if not self.success:
            raise TaskError(self)
