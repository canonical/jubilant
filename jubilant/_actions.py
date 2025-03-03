from __future__ import annotations

import dataclasses
from typing import Any, Literal


@dataclasses.dataclass(frozen=True, kw_only=True)
class ActionResult:
    """Holds the results of Juju running an action on a single unit."""

    success: bool
    """Whether the action was successful."""

    status: Literal['aborted', 'cancelled', 'completed', 'error', 'failed']
    """Status of the action (Juju operation). Typically "completed" or "failed"."""

    task_id: str
    """Task ID of the action, for use with "juju show-task"."""

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

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> ActionResult:
        status = d['status']
        results: dict[str, Any] = d.get('results') or {}
        return_code = results.pop('return-code', 0)
        stdout = results.pop('stdout', '')
        stderr = results.pop('stderr', '')
        return cls(
            success=status == 'completed',
            status=status,
            results=results,
            return_code=return_code,
            stdout=stdout,
            stderr=stderr,
            message=d.get('message') or '',
            log=d.get('log') or [],
            task_id=d['id'],
        )


class ActionError(Exception):
    """Exception raised when an action run on a single unit fails."""

    result: ActionResult
    """Results of running the action."""

    def __init__(self, result: ActionResult):
        self.result = result
