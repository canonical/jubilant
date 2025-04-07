from __future__ import annotations

import functools
import json
import logging
import os
import shlex
import shutil
import subprocess
import tempfile
import time
from collections.abc import Callable, Iterable, Mapping
from typing import Any, Literal, Union, overload

from . import _pretty, _yaml
from ._task import Task
from .statustypes import Status

logger = logging.getLogger('jubilant')


class CLIError(subprocess.CalledProcessError):
    """Subclass of ``CalledProcessError`` that includes stdout and stderr in the ``__str__``."""

    def __str__(self):
        s = super().__str__()
        if self.stdout:
            s += '\nStdout:\n' + self.stdout
        if self.stderr:
            s += '\nStderr:\n' + self.stderr
        return s


class WaitError(Exception):
    """Raised when :meth:`Juju.wait`'s *error* callable returns False."""


class SecretURI(str):
    """A string subclass that represents a secret URI ("secret:...")."""


ConfigValue = Union[bool, int, float, str, SecretURI]
"""The possible types a charm config value can be."""


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
        cli_binary: Path to the Juju CLI binary. If not specified, uses ``juju`` and assumes it is
            in the PATH.
    """

    model: str | None
    """If not None, operate on this Juju model, otherwise use the current Juju model."""

    wait_timeout: float
    """The default timeout for :meth:`wait` (in seconds) if that method's *timeout* parameter is
    not specified.
    """

    cli_binary: str
    """Path to the Juju CLI binary. If None, uses ``juju`` and assumes it is in the PATH."""

    def __init__(
        self,
        *,
        model: str | None = None,
        wait_timeout: float = 3 * 60.0,
        cli_binary: str | os.PathLike[str] | None = None,
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

    # Keep the public methods in alphabetical order, so we don't have to think
    # about where to put each new method.

    def add_model(
        self,
        model: str,
        *,
        controller: str | None = None,
        config: Mapping[str, ConfigValue] | None = None,
    ) -> None:
        """Add a named model and set this instance's model to it.

        To avoid interfering with CLI users, this won't switch the Juju CLI to the
        newly-created model. However, because :attr:`model` is set to the name of the new
        model, all subsequent operations on this instance will use the new model.

        Args:
            model: Name of model to add.
            controller: Name of controller to operate in. If not specified, use the current
                controller.
            config: Model configuration as key-value pairs, for example,
                ``{'image-stream': 'daily'}``.
        """
        args = ['add-model', '--no-switch', model]

        if controller is not None:
            args.extend(['--controller', controller])
        if config is not None:
            for k, v in config.items():
                args.extend(['--config', _format_config(k, v)])

        self.cli(*args, include_model=False)
        self.model = model

    def add_unit(
        self,
        app: str,
        *,
        attach_storage: str | Iterable[str] | None = None,
        num_units: int = 1,
        to: str | Iterable[str] | None = None,
    ):
        """Add one or more units to a deployed application.

        Args:
            app: Name of application to add units to.
            attach_storage: Existing storage(s) to attach to the deployed unit, for example,
                ``foo/0`` or ``mydisk/1``. Not available for Kubernetes models.
            num_units: Number of units to add.
            to: Machine or container to deploy the unit in (bypasses constraints). For example,
                to deploy to a new LXD container on machine 25, use ``lxd:25``.
        """
        args = ['add-unit', app]

        if attach_storage:
            if isinstance(attach_storage, str):
                args.extend(['--attach-storage', attach_storage])
            else:
                args.extend(['--attach-storage', ','.join(attach_storage)])
        if num_units != 1:
            args.extend(['--num-units', str(num_units)])
        if to:
            if isinstance(to, str):
                args.extend(['--to', to])
            else:
                args.extend(['--to', ','.join(to)])

        self.cli(*args)

    def cli(self, *args: str, include_model: bool = True, stdin: str | None = None) -> str:
        """Run a Juju CLI command and return its standard output.

        Args:
            args: Command-line arguments (excluding ``juju``).
            include_model: If true and :attr:`model` is set, insert the ``--model`` argument
                after the first argument in *args*.
            stdin: Standard input to send to the process, if any.
        """
        stdout, _ = self._cli(*args, include_model=include_model, stdin=stdin)
        return stdout

    def _cli(
        self, *args: str, include_model: bool = True, stdin: str | None = None
    ) -> tuple[str, str]:
        """Run a Juju CLI command and return its standard output and standard error."""
        if include_model and self.model is not None:
            args = (args[0], '--model', self.model) + args[1:]
        logger.info('cli: juju %s', shlex.join(args))
        try:
            process = subprocess.run(
                [self.cli_binary, *args],
                check=True,
                capture_output=True,
                encoding='utf-8',
                input=stdin,
            )
        except subprocess.CalledProcessError as e:
            raise CLIError(e.returncode, e.cmd, e.stdout, e.stderr) from None
        return (process.stdout, process.stderr)

    @overload
    def config(self, app: str, *, app_config: bool = False) -> Mapping[str, ConfigValue]: ...

    @overload
    def config(self, app: str, values: Mapping[str, ConfigValue | None]) -> None: ...

    def config(
        self,
        app: str,
        values: Mapping[str, ConfigValue | None] | None = None,
        *,
        app_config: bool = False,
    ) -> Mapping[str, ConfigValue] | None:
        """Get or set the configuration of a deployed application.

        If called with only the *app* argument, get the config and return it.
        If called with the *values* argument, set the config values and return
        ``None``.

        Args:
            app: Application name to get or set config for.
            values: Mapping of config names to values. Reset values that are
                ``None``.
            app_config: When getting config, set this to True to get the
                (poorly-named) "application-config" values instead of charm config.
        """
        if values is None:
            stdout = self.cli('config', '--format', 'json', app)
            outer = json.loads(stdout)
            inner = outer['application-config'] if app_config else outer['settings']
            result = {
                k: SecretURI(v['value']) if v['type'] == 'secret' else v['value']
                for k, v in inner.items()
                if 'value' in v
            }
            return result

        reset: list[str] = []
        args = ['config', app]
        for k, v in values.items():
            if v is None:
                reset.append(k)
            else:
                args.append(_format_config(k, v))
        if reset:
            args.extend(['--reset', ','.join(reset)])

        self.cli(*args)

    def debug_log(self, *, limit: int = 0) -> str:
        """Return debug log messages from a model.

        Args:
            limit: Limit the result to the most recent *limit* lines. Defaults to 0, meaning
                return all lines in the log.
        """
        args = ['debug-log', '--limit', str(limit)]
        return self.cli(*args)

    def deploy(
        self,
        charm: str | os.PathLike[str],
        app: str | None = None,
        *,
        attach_storage: str | Iterable[str] | None = None,
        base: str | None = None,
        channel: str | None = None,
        config: Mapping[str, ConfigValue] | None = None,
        constraints: Mapping[str, str] | None = None,
        force: bool = False,
        num_units: int = 1,
        resources: Mapping[str, str] | None = None,
        revision: int | None = None,
        storage: Mapping[str, str] | None = None,
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
            resources: Specify named resources to use for deployment, for example:
                ``{'bin': '/path/to/some/binary'}``.
            revision: Charmhub revision number to deploy.
            storage: Constraints for named storage(s), for example, ``{'data': 'tmpfs,1G'}``.
            to: Machine or container to deploy the unit in (bypasses constraints). For example,
                to deploy to a new LXD container on machine 25, use ``lxd:25``.
            trust: If true, allows charm to run hooks that require access to cloud credentials.
        """
        args = ['deploy', str(charm)]
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
        if resources is not None:
            for k, v in resources.items():
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

    def destroy_model(
        self,
        model: str,
        *,
        destroy_storage: bool = False,
        force: bool = False,
    ) -> None:
        """Terminate all machines (or containers) and resources for a model.

        If the given model is this instance's model, also sets this instance's
        :attr:`model` to None.

        Args:
            model: Name of model to destroy.
            destroy_storage: If true, destroy all storage instances in the model.
            force: If true, force model destruction and ignore any errors.
        """
        args = ['destroy-model', model, '--no-prompt']
        if destroy_storage:
            args.append('--destroy-storage')
        if force:
            args.append('--force')
        self.cli(*args, include_model=False)
        if model == self.model:
            self.model = None

    @overload
    def exec(self, *command: str, machine: int, wait: float | None = None) -> Task: ...

    @overload
    def exec(self, *command: str, unit: str, wait: float | None = None) -> Task: ...

    def exec(
        self,
        *command: str,
        machine: int | None = None,
        unit: str | None = None,
        wait: float | None = None,
    ) -> Task:
        """Run the command on the remote target specified.

        You must specify either *machine* or *unit*, but not both.

        Note: this method does not support running a command on multiple units
        at once. If you need that, let us know, and we'll consider adding it
        with a new ``exec_multiple`` method or similar.

        Args:
            command: Command to run, along with its arguments.
            machine: ID of machine to run the command on.
            unit: Name of unit to run the command on, for example ``mysql/0`` or ``mysql/leader``.
            wait: Maximum time to wait for command to finish; :class:`TimeoutError` is raised if
                this is reached. Default is to wait indefinitely.

        Returns:
            The task created to run the command, including logs, failure message, and so on.

        Raises:
            ValueError: if the machine or unit doesn't exist.
            TaskError: if the command failed.
            TimeoutError: if *wait* was specified and the wait time was reached.
        """
        if (machine is not None and unit is not None) or (machine is None and unit is None):
            raise TypeError('must specify "machine" or "unit", but not both')

        args = ['exec', '--format', 'json']
        if machine is not None:
            args.extend(['--machine', str(machine)])
        else:
            assert unit is not None
            args.extend(['--unit', unit])
        if wait is not None:
            args.extend(['--wait', f'{wait}s'])
        args.append('--')
        args.extend(command)

        try:
            stdout, stderr = self._cli(*args)
        except CLIError as exc:
            if 'timed out' in exc.stderr:
                msg = f'timed out waiting for command, stderr:\n{exc.stderr}'
                raise TimeoutError(msg) from None
            # The "juju exec" CLI command itself fails if the exec'd command fails.
            if 'task failed' not in exc.stderr:
                raise
            stdout = exc.stdout
            stderr = exc.stderr

        # Command doesn't return any stdout if no units exist.
        results: dict[str, Any] = json.loads(stdout) if stdout.strip() else {}
        if machine is not None:
            if str(machine) not in results:
                raise ValueError(f'machine {machine!r} not found, stderr:\n{stderr}')
            result = results[str(machine)]
        else:
            if unit not in results:
                raise ValueError(f'unit {unit!r} not found, stderr:\n{stderr}')
            result = results[unit]
        task = Task._from_dict(result)
        task.raise_on_failure()
        return task

    def integrate(self, app1: str, app2: str, *, via: str | Iterable[str] | None = None) -> None:
        """Integrate two applications, creating a relation between them.

        The order of *app1* and *app2* is not significant. Each of them should
        be in the format ``<application>[:<endpoint>]``. The endpoint is only
        required if there's more than one possible integration between the two
        applications.

        To integrate an application in the current model with an application in
        another model (cross-model), prefix *app1* or *app2* with ``<model>.``.
        To integrate with an application on another controller, *app1* or *app2* must
        be an offer endpoint. See ``juju integrate --help`` for details.

        Args:
            app1: One of the applications (and endpoints) to integrate.
            app2: The other of the applications (and endpoints) to integrate.
            via: Inform the offering side (the remote application) of the
                source of traffic, to enable network ports to be opened. This
                is in CIDR notation, for example ``192.0.2.0/24``.
        """
        args = ['integrate', app1, app2]
        if via:
            if isinstance(via, str):
                args.extend(['--via', via])
            else:
                args.extend(['--via', ','.join(via)])
        self.cli(*args)

    def remove_relation(self, app1: str, app2: str, *, force: bool = False) -> None:
        """Remove an existing relation between two applications (opposite of :meth:`integrate`).

        The order of *app1* and *app2* is not significant. Each of them should
        be in the format ``<application>[:<endpoint>]``. The endpoint is only
        required if there's more than one possible integration between the two
        applications.

        Args:
            app1: One of the applications (and endpoints) to integrate.
            app2: The other of the applications (and endpoints) to integrate.
            force: Force removal, ignoring operational errors.
        """
        args = ['remove-relation', app1, app2]
        if force:
            args.append('--force')
        self.cli(*args)

    def remove_unit(
        self,
        *app_or_unit: str,
        destroy_storage: bool = False,
        force: bool = False,
        num_units: int = 0,
    ) -> None:
        """Remove application units from the model.

        Examples::

            # Kubernetes model:
            juju.remove_unit('wordpress', num_units=2)

            # Machine model:
            juju.remove_unit('wordpress/1')
            juju.remove_unit('wordpress/2', 'wordpress/3')

        Args:
            app_or_unit: On machine models, this is the name of the unit or units to remove.
                On Kubernetes models, this is actually the application name (a single string),
                as individual units are not named; you must use *num_units* to remove more than
                one unit on a Kubernetes model.
            destroy_storage: If True, also destroy storage attached to units.
            force: Force removal even if a unit is in an error state.
            num_units: Number of units to remove (Kubernetes models only).
        """
        args = ['remove-unit', '--no-prompt', *app_or_unit]

        if destroy_storage:
            args.append('--destroy-storage')
        if force:
            args.append('--force')
        if num_units:
            if len(app_or_unit) > 1:
                raise TypeError('"app_or_unit" must be a single app name if num_units specified')
            args.extend(['--num-units', str(num_units)])

        self.cli(*args)

    def run(
        self,
        unit: str,
        action: str,
        params: Mapping[str, Any] | None = None,
        *,
        wait: float | None = None,
    ) -> Task:
        """Run an action on the given unit and wait for the result.

        Note: this method does not support running an action on multiple units
        at once. If you need that, let us know, and we'll consider adding it
        with a new ``run_multiple`` method or similar.

        Example::

            juju = jubilant.Juju()
            result = juju.run('mysql/0', 'get-password')
            assert result.results['username'] == 'USER0'

        Args:
            unit: Name of unit to run the action on, for example ``mysql/0`` or
                ``mysql/leader``.
            action: Name of action to run.
            params: Optional named parameters to pass to the action.
            wait: Maximum time to wait for action to finish; :class:`TimeoutError` is raised if
                this is reached. Default is to wait indefinitely.

        Returns:
            The task created to run the action, including logs, failure message, and so on.

        Raises:
            ValueError: if the action or the unit doesn't exist.
            TaskError: if the action failed.
            TimeoutError: if *wait* was specified and the wait time was reached.
        """
        args = ['run', '--format', 'json', unit, action]
        if wait is not None:
            args.extend(['--wait', f'{wait}s'])

        params_file = None
        if params is not None:
            with tempfile.NamedTemporaryFile(
                'w+', delete=False, dir=self._temp_dir
            ) as params_file:
                _yaml.safe_dump(params, params_file)
            args.extend(['--params', params_file.name])

        try:
            try:
                stdout, stderr = self._cli(*args)
            except CLIError as exc:
                if 'timed out' in exc.stderr:
                    msg = f'timed out waiting for action, stderr:\n{exc.stderr}'
                    raise TimeoutError(msg) from None
                # The "juju run" CLI command fails if the action has an uncaught exception.
                if 'task failed' not in exc.stderr:
                    raise
                stdout = exc.stdout
                stderr = exc.stderr

            # Command doesn't return any stdout if no units exist.
            all_tasks: dict[str, Any] = json.loads(stdout) if stdout.strip() else {}
            if unit not in all_tasks:
                raise ValueError(
                    f'action {action!r} not defined or unit {unit!r} not found, stderr:\n{stderr}'
                )
            task = Task._from_dict(all_tasks[unit])
            task.raise_on_failure()
            return task
        finally:
            if params_file is not None:
                os.remove(params_file.name)

    def status(self) -> Status:
        """Fetch the status of the current model, including its applications and units."""
        stdout = self.cli('status', '--format', 'json')
        result = json.loads(stdout)
        return Status._from_dict(result)

    def trust(
        self, app: str, *, remove: bool = False, scope: Literal['cluster'] | None = None
    ) -> None:
        """Set the trust status of a deployed application.

        Args:
            app: Application name to set trust status for.
            remove: Set to True to remove trust status.
            scope: On Kubernetes models, this must be set to "cluster", as the trust operation
                grants the charm full access to the cluster.
        """
        args = ['trust', app]
        if remove:
            args.append('--remove')
        if scope is not None:
            args.extend(['--scope', scope])

        self.cli(*args)

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
            timeout: Overall timeout; :class:`TimeoutError` is raised if this is reached.
                If not specified, uses the *wait_timeout* specified when the instance was created.
            successes: Number of times *ready* must return true for the wait to succeed.

        Raises:
            TimeoutError: If the *timeout* is reached. A string representation
                of the last status, if any, is added as an exception note.
            WaitError: If the *error* callable returns True. A string representation
                of the last status is added as an exception note.
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
                logger.info('wait: status changed:\n%s', _status_diff(prev_status, status))

            if error is not None and error(status):
                raise WaitError(f'error function {error.__qualname__} returned false\n{status}')

            if ready(status):
                success_count += 1
                if success_count >= successes:
                    return status
            else:
                success_count = 0

            time.sleep(delay)

        if status is None:
            raise TimeoutError(f'wait timed out after {timeout}s')
        raise TimeoutError(f'wait timed out after {timeout}s\n{status}')

    @functools.cached_property
    def _juju_is_snap(self) -> bool:
        which = shutil.which(self.cli_binary)
        return which is not None and '/snap/' in which

    @functools.cached_property
    def _temp_dir(self) -> str:
        if self._juju_is_snap:
            # If Juju is running as a snap, we can't use /tmp, so put temp files here instead.
            temp_dir = os.path.expanduser('~/snap/juju/common')
            os.makedirs(temp_dir, exist_ok=True)
            return temp_dir
        else:
            return tempfile.gettempdir()


def _format_config(k: str, v: ConfigValue) -> str:
    if isinstance(v, bool):
        v = 'true' if v else 'false'
    return f'{k}={v}'


def _status_diff(old: Status | None, new: Status) -> str:
    """Return a line-based diff of two status objects."""
    if old is None:
        old_lines = []
    else:
        old_lines = [line for line in _pretty.gron(old) if _status_line_ok(line)]
    new_lines = [line for line in _pretty.gron(new) if _status_line_ok(line)]
    return '\n'.join(_pretty.diff(old_lines, new_lines))


def _status_line_ok(line: str) -> bool:
    """Return whether the status line should be included in the diff."""
    # Exclude controller timestamp as it changes every update and is just noise.
    field, _, _ = line.partition(' = ')
    if field == '.controller.timestamp':
        return False
    # Exclude status-updated-since timestamps as they just add noise (and log lines already
    # include timestamps).
    if field.endswith('.since'):
        return False
    return True
