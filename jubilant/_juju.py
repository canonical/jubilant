import json
import os
import subprocess
import time
import typing

from ._errors import CLIError, WaitError
from ._helpers import any_error
from ._types import Status


class Juju:
    """TODO."""

    def __init__(
        self,
        *,
        model: str | None = None,
        juju_bin: os.PathLike | None = None,
    ):
        self.model = model
        self.juju_bin = juju_bin or 'juju'

    def __repr__(self):
        args = []
        if self.model is not None:
            args.append(f'model={self.model!r}')
        return f'Juju({", ".join(args)})'

    def cli(self, *args: str) -> str:
        """."""
        try:
            process = subprocess.run(
                [self.juju_bin, *args], check=True, capture_output=True, encoding='UTF-8'
            )
        except subprocess.CalledProcessError as e:
            raise CLIError(e.returncode, e.cmd, e.stdout, e.stderr) from None
        return process.stdout

    def add_model(
        self,
        model_name: str,  # TODO: should this use self.model if set, and set it if not?
        *,
        controller: str | None = None,
        config: dict[str, typing.Any] | None = None,  # TODO: is Any correct here?
    ) -> None:
        """TODO."""
        args = ['add-model', model_name]

        if controller is not None:
            args.extend(['--controller', controller])
        if config is not None:
            for k, v in config.items():
                args.extend(['--config', f'{k}={v}'])

        self.cli(*args)

    def destroy_model(
        self,
        model_name: str,
        *,
        force=False,
    ):
        """TODO."""
        args = ['destroy-model', model_name, '--no-prompt']
        if force:
            args.append('--force')
        self.cli(*args)

    def deploy(
        self,
        charm_name: str,
        application_name: str | None = None,
        *,
        model: str | None = None,
        config: dict[str, typing.Any] | None = None,  # TODO: is Any correct here?
        num_units: int = 1,
        resources: dict[str, str] | None = None,
        trust: bool = False,
        # TODO: include all the arguments we think people we use
    ) -> None:
        """TODO."""
        args = ['deploy', charm_name]
        if application_name is not None:
            args.append(application_name)

        if model is None:
            model = self.model
        if model is not None:
            args.extend(['--model', model])
        if config is not None:
            for k, v in config.items():
                args.extend(['--config', f'{k}={v}'])
        if num_units != 1:
            args.extend(['--num-units', str(num_units)])
        if resources is not None:
            for k, v in resources.items():
                args.extend(['--resource', f'{k}={v}'])
        if trust:
            args.append('--trust')

        self.cli(*args)

    def status(
        self,
        *,
        model: str | None = None,
    ) -> Status:
        """TODO."""
        args = ['status', '--format', 'json']

        if model is None:
            model = self.model
        if model is not None:
            args.extend(['--model', model])

        stdout = self.cli(*args)
        result = json.loads(stdout)
        return Status.from_dict(result)

    def wait(
        self,
        ready: typing.Callable[[Status], bool],
        *,
        model: str | None = None,
        # TODO: should this callable raise instead? maybe better errors
        error: typing.Callable[[Status], bool] = any_error,
        delay: float = 1.0,
        timeout: float = 10 * 60.0,
        successes: int = 3,
    ) -> Status:
        """Wait until ``ready(status)`` returns true, *successes* times in a row.

        This fetches the Juju status repeatedly (waiting *delay* seconds between each call),
        and returns the last status after the *ready* callable returns true a number
        of times in a row (*successes* times).

        Args:
            ready: Callable that takes a :class:`Status` object and returns true when the wait
                should be considered ready. It needs to return true *successes* times in a row
                before ``wait`` returns.
            model: Juju model name. Overrides ``self.model`` if that is set.
            error: Callable that takes a :class:`Status` object and returns true when ``wait``
                should raise an error (*WaitError*).
            delay: Delay in seconds between status calls.
            timeout: Overall timeout; *TimeoutError* is raised when this is reached.
            successes: Number of times *ready* must return true for ``wait`` to succeed.

        Raises:
            TimeoutError: If the *timeout* is reached.
            WaitError: If the *error* callable returns true.
        """
        success_count = 0
        status = None
        start = time.monotonic()

        while time.monotonic() - start < timeout:
            status = self.status(model=model)
            # TODO: ensure better debugging, eg: log when status changed
            print('TODO wait', status)

            if error(status):
                raise WaitError(f'error function ({error}) returned false, last status:\n{status}')

            if ready(status):
                success_count += 1
                if success_count >= successes:
                    return status
            else:
                success_count = 0

            time.sleep(delay)

        raise TimeoutError(f'timed out after {timeout}, last status:\n{status}')
