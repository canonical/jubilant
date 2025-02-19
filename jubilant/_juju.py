import json
import logging
import os
import subprocess
import time
from collections.abc import Callable, Iterable

from .statustypes import Status

logger = logging.getLogger('jubilant')


class CLIError(subprocess.CalledProcessError):
    """Subclass of CalledProcessError that includes stdout and stderr in the __str__."""

    def __str__(self):
        s = super().__str__()
        if self.stdout:
            s += '\nStdout:\n' + self.stdout
        if self.stderr:
            s += '\nStderr:\n' + self.stderr
        return s


class WaitError(Exception):
    """Raised when :meth:`Juju.wait`'s "error" callable returns False."""


class Juju:
    """Instantiate this class to run Juju commands.

    Most methods directly call a single Juju CLI command. If a CLI command doesn't yet exist as a
    method, use :meth:`cli`.

    Example::

        juju = jubilant.Juju()
        juju.deploy('snappass-test')

    Args:
        model: If specified, operate on this Juju model, otherwise use the current Juju model.
        wait_timeout: The default timeout for :meth:`wait` (in seconds) if that method's *timeout*
            parameter is not specified.
        cli_binary: Path to the Juju CLI binary. If not specified, uses "juju" and assumes it is
            in the PATH.
    """

    model: str | None
    """If not None, operate on this Juju model, otherwise use the current Juju model."""

    wait_timeout: float
    """The default timeout for :meth:`wait` (in seconds) if that method's *timeout* parameter is
    not specified.
    """

    cli_binary: str
    """Path to the Juju CLI binary. If None, uses "juju" and assumes it is in the PATH."""

    def __init__(
        self,
        *,
        model: str | None = None,
        wait_timeout: float = 3 * 60.0,
        cli_binary: str | os.PathLike | None = None,
    ):
        self.model = model
        self.wait_timeout = wait_timeout
        self.cli_binary = str(cli_binary or 'juju')

    def __repr__(self) -> str:
        args = [
            f'model={self.model!r}',
            f'wait_timeout={self.wait_timeout}',
            f'cli_binary={self.cli_binary!r}',
        ]
        return f'Juju({", ".join(args)})'

    def cli(self, *args: str, include_model: bool = True) -> str:
        """Run a Juju CLI command and return its standard output.

        Args:
            args: Command-line arguments (excluding "juju").
            include_model: If true and :attr:`model` is set, insert the ``--model`` argument
                after the first argument in *args*.
        """
        if include_model and self.model is not None:
            args = (args[0], '--model', self.model) + args[1:]
        try:
            process = subprocess.run(
                [self.cli_binary, *args], check=True, capture_output=True, encoding='UTF-8'
            )
        except subprocess.CalledProcessError as e:
            raise CLIError(e.returncode, e.cmd, e.stdout, e.stderr) from None
        return process.stdout

    def add_model(
        self,
        model: str,
        *,
        controller: str | None = None,
        config: dict[str, bool | int | float | str] | None = None,
    ) -> None:
        """Add a named model and set this instance's model to it.

        Args:
            model: Name of model to add.
            controller: Name of controller to operate in. If not specified, use the current
                controller.
            config: Model configuration as key-value pairs, for example,
                ``{'image-stream': 'daily'}``.
        """
        args = ['add-model', model]

        if controller is not None:
            args.extend(['--controller', controller])
        if config is not None:
            for k, v in config.items():
                args.extend(['--config', _format_config(k, v)])

        self.cli(*args, include_model=False)
        self.model = model

    def switch(self, model: str) -> None:
        """Switch to a named model and set this instance's model to it.

        Args:
            model: Name of model to switch to. This can be a model name, a controller name, or in
                ``mycontroller:mymodel`` syntax.
        """
        self.cli('switch', model, include_model=False)
        self.model = model

    def destroy_model(
        self,
        model: str,
        *,
        force=False,
    ) -> None:
        """Terminate all machines (or containers) and resources for a model.

        Also sets this instance's :attr:`model` to None, meaning use the current Juju model for
        subsequent commands.

        Args:
            model: Name of model to destroy.
            force: If true, force model destruction and ignore any errors.
        """
        args = ['destroy-model', model, '--no-prompt']
        if force:
            args.append('--force')
        self.cli(*args, include_model=False)
        self.model = None

    def deploy(
        self,
        charm: str | os.PathLike,
        app: str | None = None,
        *,
        attach_storage: str | Iterable[str] | None = None,
        base: str | None = None,
        channel: str | None = None,
        config: dict[str, bool | int | float | str] | None = None,
        constraints: dict[str, str] | None = None,
        force: bool = False,
        num_units: int = 1,
        resource: dict[str, str] | None = None,
        revision: int | None = None,
        storage: dict[str, str] | None = None,
        to: str | Iterable[str] | None = None,
        trust: bool = False,
    ) -> None:
        """Deploy an application or bundle.

        Args:
            charm: Name of charm or bundle to deploy, or path to a local file (must start with
                ``/`` or ``.``).
            app: Optional application name within the model; defaults to the charm name.
            attach_storage: Existing storage(s) to attach to the deployed unit, for example,
                ``foo/0`` or ``mydisk/1``. Not available for Kubernetes models.
            base: The base on which to deploy, for example, ``ubuntu@22.04``.
            channel: Channel to use when deploying from Charmhub, for example, ``latest/edge``.
            config: Application configuration as key-value pairs, for example,
                ``{'name': 'My Wiki'}``.
            constraints: Hardware constraints for new machines, for example, ``{'mem': '8G'}``.
            force: If true, bypass checks such as supported bases.
            num_units: Number of units to deploy for principal charms.
            resource: Specify named resources to use for deployment, for example:
                ``{'bin': '/path/to/some/binary'}``.
            revision: Charmhub revision number to deploy.
            storage: Constraints for named storage(s), for example, ``{'data': 'tmpfs,1G'}``.
            to: Machine or container to deploy the unit in (bypasses constraints). For example,
                to deploy to a new LXD container on machine 25, use ``lxd:25``.
            trust: If true, allows charm to run hooks that require access to cloud credentials.
        """
        args = ['deploy', charm]
        if app is not None:
            args.append(app)

        if attach_storage:
            if isinstance(attach_storage, str):
                args.extend(['--attach-storage', attach_storage])
            else:
                args.extend(['--attach-storage', ','.join(attach_storage)])
        if base is not None:
            args.extend(['--base', base])
        if channel is not None:
            args.extend(['--channel', channel])
        if config is not None:
            for k, v in config.items():
                args.extend(['--config', _format_config(k, v)])
        if constraints is not None:
            for k, v in constraints.items():
                args.extend(['--constraints', f'{k}={v}'])
        if force:
            args.append('--force')
        if num_units != 1:
            args.extend(['--num-units', str(num_units)])
        if resource is not None:
            for k, v in resource.items():
                args.extend(['--resource', f'{k}={v}'])
        if revision is not None:
            args.extend(['--revision', str(revision)])
        if storage is not None:
            for k, v in storage.items():
                args.extend(['--storage', f'{k}={v}'])
        if to:
            if isinstance(to, str):
                args.extend(['--to', to])
            else:
                args.extend(['--to', ','.join(to)])
        if trust:
            args.append('--trust')

        self.cli(*args)

    def status(self) -> Status:
        """Fetch the status of the current model, including its applications and units."""
        args = ['status', '--format', 'json']
        stdout = self.cli(*args)
        result = json.loads(stdout)
        return Status._from_dict(result)

    def wait(
        self,
        ready: Callable[[Status], bool],
        *,
        error: Callable[[Status], bool] | None = None,
        delay: float = 1.0,
        timeout: float | None = None,
        successes: int = 3,
    ) -> Status:
        """Wait until ``ready(status)`` returns true.

        This fetches the Juju status repeatedly (waiting *delay* seconds between each call),
        and returns the last status after the *ready* callable returns true for *successes*
        times in a row.

        This function logs the status object after the first status call, and after subsequent
        calls if the status object has changed.

        Example::

            juju = jubilant.Juju()
            juju.deploy('snappass-test')
            juju.wait(
                lambda status: status.apps['snappass-test'].is_active,
                error=jubilant.any_error,
            )

        Args:
            ready: Callable that takes a :class:`Status` object and returns true when the wait
                should be considered ready. It needs to return true *successes* times in a row
                before ``wait`` returns.
            error: Callable that takes a :class:`Status` object and returns true when ``wait``
                should raise an error (:class:`WaitError`).
            delay: Delay in seconds between status calls.
            timeout: Overall timeout; :class:`TimeoutError` is raised when this is reached.
                If not specified, uses the *wait_timeout* specified when the instance was created.
            successes: Number of times *ready* must return true for the wait to succeed.

        Raises:
            TimeoutError: If the *timeout* is reached.
            WaitError: If the *error* callable returns True.
        """
        if timeout is None:
            timeout = self.wait_timeout

        status = None
        success_count = 0
        start = time.monotonic()

        while time.monotonic() - start < timeout:
            prev_status = status
            status = self.status()
            if status != prev_status:
                logger.info('status changed:\n%s', status)

            if error is not None and error(status):
                msg = f'error function {error.__qualname__} returned false'
                raise _exception_with_status(WaitError, msg, status)

            if ready(status):
                success_count += 1
                if success_count >= successes:
                    return status
            else:
                success_count = 0

            time.sleep(delay)

        raise _exception_with_status(TimeoutError, f'timed out after {timeout}s', status)


def _exception_with_status(
    exc_type: type[Exception], msg: str, status: Status | None
) -> Exception:
    if status is None:
        return exc_type(msg)
    if hasattr(exc_type, 'add_note'):  # available in Python 3.11+ (PEP 678)
        exc = exc_type(msg)
        exc.add_note(str(status))
        return exc
    else:
        return exc_type(msg + '\n' + str(status))


def _format_config(k: str, v: bool | int | float | str) -> str:
    if isinstance(v, bool):
        v = 'true' if v else 'false'
    return f'{k}={v}'
