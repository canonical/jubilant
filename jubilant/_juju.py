from __future__ import annotations

import functools
import json
import logging
import os
import pathlib
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
logger_wait = logging.getLogger('jubilant.wait')


class CLIError(subprocess.CalledProcessError):
    """Subclass of ``CalledProcessError`` that includes stdout and stderr in the ``__str__``."""

    def __str__(self) -> str:
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

    @property
    def unique_identifier(self) -> str:
        """Unique identifier of this secret URI.

        This is the secret's globally-unique identifier (currently a 20-character Xid,
        for example "9m4e2mr0ui3e8a215n4g").
        """
        if '/' in self:
            # Handle 'secret://MODEL-UUID/UNIQUE-IDENTIFIER'
            return self.rsplit('/', maxsplit=1)[-1]
        elif self.startswith('secret:'):
            # Handle common case of 'secret:UNIQUE-IDENTIFIER'
            return self[len('secret:') :]
        else:
            return str(self)


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
            If the model is in another controller, prefix the model name with ``<controller>:``.
        wait_timeout: The default timeout for :meth:`wait` (in seconds) if that method's *timeout*
            parameter is not specified.
        cli_binary: Path to the Juju CLI binary. If not specified, uses ``juju`` and assumes it is
            in the PATH.
    """

    model: str | None
    """If not None, operate on this Juju model, otherwise use the current Juju model.

    If the model is in another controller, prefix the model name with ``<controller>:``; for
    example, ``juju = jubilant.Juju(model='mycontroller:my-model')``.
    """

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
        cli_binary: str | pathlib.Path | None = None,
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
        cloud: str | None = None,
        *,
        controller: str | None = None,
        config: Mapping[str, ConfigValue] | None = None,
        credential: str | None = None,
    ) -> None:
        """Add a named model and set this instance's model to it.

        To avoid interfering with CLI users, this won't switch the Juju CLI to the
        newly-created model. However, because :attr:`model` is set to the name of the new
        model, all subsequent operations on this instance will use the new model.

        Args:
            model: Name of model to add.
            cloud: Name of cloud or region (or cloud/region) to use for the model.
            controller: Name of controller to operate in. If not specified, use the current
                controller.
            config: Model configuration as key-value pairs, for example,
                ``{'image-stream': 'daily'}``.
            credential: Name of cloud credential to use for the model.
        """
        args = ['add-model', '--no-switch', model]

        if cloud is not None:
            args.append(cloud)

        if controller is None:
            model_name = model
        else:
            args.extend(['--controller', controller])
            model_name = f'{controller}:{model}'
        if config is not None:
            for k, v in config.items():
                args.extend(['--config', _format_config(k, v)])
        if credential is not None:
            args.extend(['--credential', credential])

        self.cli(*args, include_model=False)
        self.model = model_name

    def add_secret(
        self,
        name: str,
        content: Mapping[str, str],
        *,
        info: str | None = None,
    ) -> SecretURI:
        """Add a new named secret and returns its secret URI.

        Args:
            name: Name for the secret.
            content: Key-value pairs that represent the secret content, for example
                ``{'password': 'hunter2'}``.
            info: Optional description for the secret.
        """
        args = ['add-secret', name]
        if info is not None:
            args.extend(['--info', info])

        with tempfile.NamedTemporaryFile('w+', dir=self._temp_dir) as file:
            _yaml.safe_dump(content, file)
            file.flush()
            args.extend(['--file', file.name])
            output = self.cli(*args)

        return SecretURI(output.strip())

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
        self, *args: str, include_model: bool = True, stdin: str | None = None, log: bool = True
    ) -> tuple[str, str]:
        """Run a Juju CLI command and return its standard output and standard error."""
        if include_model and self.model is not None:
            args = (args[0], '--model', self.model) + args[1:]
        if log:
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
    def config(
        self,
        app: str,
        values: Mapping[str, ConfigValue],
        *,
        reset: str | Iterable[str] = (),
    ) -> None: ...

    @overload
    def config(self, app: str, *, reset: str | Iterable[str]) -> None: ...

    def config(
        self,
        app: str,
        values: Mapping[str, ConfigValue] | None = None,
        *,
        app_config: bool = False,
        reset: str | Iterable[str] = (),
    ) -> Mapping[str, ConfigValue] | None:
        """Get or set the configuration of a deployed application.

        If called with only the *app* argument, get the config and return it.

        If called with the *values* or *reset* arguments, set the config values and return None,
        and reset any keys in *reset* to their defaults.

        Args:
            app: Application name to get or set config for.
            values: Mapping of config names to values to set.
            app_config: When getting config, set this to True to get the
                (poorly-named) "application-config" values instead of charm config.
            reset: Key or list of keys to reset to their defaults.
        """
        if values is None and not reset:
            stdout = self.cli('config', '--format', 'json', app)
            outer = json.loads(stdout)
            inner = outer['application-config'] if app_config else outer['settings']
            result = {
                k: SecretURI(v['value']) if v['type'] == 'secret' else v['value']
                for k, v in inner.items()
                if 'value' in v
            }
            return result

        args = ['config', app]
        if values:
            args.extend(_format_config(k, v) for k, v in values.items())
        if reset:
            if not isinstance(reset, str):
                reset = ','.join(reset)
            args.extend(['--reset', reset])

        self.cli(*args)

    def consume(
        self,
        model_and_app: str,
        alias: str | None = None,
        *,
        controller: str | None = None,
        owner: str | None = None,
    ) -> None:
        """Add a remote offer to the model.

        Examples::

            juju.consume('othermodel.mysql', 'sql')
            juju.consume('othermodel.mysql', controller='ctrl2', owner='admin')

        Args:
            model_and_app: Dotted application and model name to offer endpoints for, for example
                ``othermodel.mysql``.
            alias: A local alias for the offer, for use with :meth:`integrate`. Defaults to the
                application name.
            controller: Remote offer's controller. Defaults to the current controller.
            owner: Remote model's owner. Defaults to the user that is currently logged in to the
                controller providing the offer.
        """
        offer_path = model_and_app
        if owner is not None:
            offer_path = f'{owner}/{offer_path}'
        if controller is not None:
            offer_path = f'{controller}:{offer_path}'
        args = ['consume', offer_path]
        if alias is not None:
            args.append(alias)

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
        charm: str | pathlib.Path,
        app: str | None = None,
        *,
        attach_storage: str | Iterable[str] | None = None,
        base: str | None = None,
        bind: Mapping[str, str] | str | None = None,
        channel: str | None = None,
        config: Mapping[str, ConfigValue] | None = None,
        constraints: Mapping[str, str] | None = None,
        force: bool = False,
        num_units: int = 1,
        overlays: Iterable[str | pathlib.Path] = (),
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
            app: Optional application name within the model. Defaults to the charm name.
            attach_storage: Existing storage(s) to attach to the deployed unit, for example,
                ``foo/0`` or ``mydisk/1``. Not available for Kubernetes models.
            base: The base on which to deploy, for example, ``ubuntu@22.04``.
            bind: Either a mapping of endpoint-to-space bindings, for example
                ``{'database-peers': 'internal-space'}``, or a single space name, which is
                equivalent to binding all endpoints to that space.
            channel: Channel to use when deploying from Charmhub, for example, ``latest/edge``.
            config: Application configuration as key-value pairs, for example,
                ``{'name': 'My Wiki'}``.
            constraints: Hardware constraints for new machines, for example, ``{'mem': '8G'}``.
            force: If true, bypass checks such as supported bases.
            num_units: Number of units to deploy for principal charms.
            overlays: File paths of bundles to overlay on the primary bundle, applied in order.
            resources: Specify named resources to use for deployment, for example:
                ``{'bin': '/path/to/some/binary'}``.
            revision: Charmhub revision number to deploy.
            storage: Constraints for named storage(s), for example, ``{'data': 'tmpfs,1G'}``.
            to: Machine or container to deploy the unit in (bypasses constraints). For example,
                to deploy to a new LXD container on machine 25, use ``lxd:25``.
            trust: If true, allows charm to run hooks that require access to cloud credentials.
        """
        # Need this check because str is also an iterable of str.
        if isinstance(overlays, str):
            raise TypeError('overlays must be an iterable of str or pathlib.Path, not str')

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
        if bind is not None:
            if not isinstance(bind, str):
                bind = ' '.join(f'{k}={v}' for k, v in bind.items())
            args.extend(['--bind', bind])
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
        for overlay in overlays:
            args.extend(['--overlay', str(overlay)])
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
    def exec(self, command: str, *args: str, machine: int, wait: float | None = None) -> Task: ...

    @overload
    def exec(self, command: str, *args: str, unit: str, wait: float | None = None) -> Task: ...

    def exec(
        self,
        command: str,
        *args: str,
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
            command: Command to run. Because the command is executed using the shell,
                arguments may also be included here as a single string, for example
                ``juju.exec('echo foo', ...)``.
            args: Arguments of the command.
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

        cli_args = ['exec', '--format', 'json']
        if machine is not None:
            cli_args.extend(['--machine', str(machine)])
        else:
            assert unit is not None
            cli_args.extend(['--unit', unit])
        if wait is not None:
            cli_args.extend(['--wait', f'{wait}s'])
        cli_args.append('--')
        cli_args.append(command)
        cli_args.extend(args)

        try:
            stdout, stderr = self._cli(*cli_args)
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

    @overload
    def model_config(self) -> Mapping[str, ConfigValue]: ...

    @overload
    def model_config(
        self, values: Mapping[str, ConfigValue], *, reset: str | Iterable[str] = ()
    ) -> None: ...

    @overload
    def model_config(self, *, reset: str | Iterable[str]) -> None: ...

    def model_config(
        self, values: Mapping[str, ConfigValue] | None = None, reset: str | Iterable[str] = ()
    ) -> Mapping[str, ConfigValue] | None:
        """Get or set the configuration of the model.

        If called with no arguments, get the model config and return it.

        If called with the *values* or *reset* arguments, set the model config values and return
        None, and reset any keys in *reset* to their defaults.

        Args:
            values: Mapping of model config names to values to set, for example
                ``{'update-status-hook-interval': '10s'}``.
            reset: Key or list of keys to reset to their defaults.
        """
        if values is None and not reset:
            stdout = self.cli('model-config', '--format', 'json')
            result = json.loads(stdout)
            return {k: v['Value'] for k, v in result.items() if 'Value' in v}

        args = ['model-config']
        if values:
            args.extend(_format_config(k, v) for k, v in values.items())
        if reset:
            if not isinstance(reset, str):
                reset = ','.join(reset)
            args.extend(['--reset', reset])

        self.cli(*args)

    def offer(
        self,
        app: str,
        *,
        controller: str | None = None,
        endpoint: str | Iterable[str],
        name: str | None = None,
    ) -> None:
        """Offer application endpoints for use in other models.

        Examples::

            juju.offer('mysql', endpoint='db')
            juju.offer('mymodel.mysql', endpoint=['db', 'log'], name='altname')

        Args:
            app: Application name to offer endpoints for. May include a dotted model name, for
                example ``mymodel.mysql``.
            controller: Name of controller to operate in. If not specified, use the current
                controller.
            endpoint: Endpoint or endpoints to offer.
            name: Name of the offer. By default, the offer is named after the application.
        """
        if not isinstance(endpoint, str):
            endpoint = ','.join(endpoint)
        app_endpoint = f'{app}:{endpoint}'
        args = ['offer', app_endpoint]
        if controller:
            args.extend(['--controller', controller])
        if name is not None:
            args.append(name)

        self.cli(*args, include_model=False)

    def refresh(
        self,
        app: str,
        *,
        base: str | None = None,
        channel: str | None = None,
        config: Mapping[str, ConfigValue] | None = None,
        force: bool = False,
        path: str | pathlib.Path | None = None,
        resources: Mapping[str, str] | None = None,
        revision: int | None = None,
        storage: Mapping[str, str] | None = None,
        trust: bool = False,
    ):
        """Refresh (upgrade) an application's charm.

        Args:
            app: Name of application to refresh.
            base: Select a different base than is currently running.
            channel: Channel to use when deploying from Charmhub, for example, ``latest/edge``.
            config: Application configuration as key-value pairs.
            force: If true, bypass checks such as supported bases.
            path: Refresh to a charm located at this path.
            resources: Specify named resources to use for deployment, for example:
                ``{'bin': '/path/to/some/binary'}``.
            revision: Charmhub revision number to deploy.
            storage: Constraints for named storage(s), for example, ``{'data': 'tmpfs,1G'}``.
            trust: If true, allows charm to run hooks that require access to cloud credentials.
        """
        args = ['refresh', app]

        if base is not None:
            args.extend(['--base', base])
        if channel is not None:
            args.extend(['--channel', channel])
        if config is not None:
            for k, v in config.items():
                args.extend(['--config', _format_config(k, v)])
        if force:
            args.extend(['--force', '--force-base', '--force-units'])
        if path is not None:
            args.extend(['--path', str(path)])
        if resources is not None:
            for k, v in resources.items():
                args.extend(['--resource', f'{k}={v}'])
        if revision is not None:
            args.extend(['--revision', str(revision)])
        if storage is not None:
            for k, v in storage.items():
                args.extend(['--storage', f'{k}={v}'])
        if trust:
            args.append('--trust')

        self.cli(*args)

    def remove_application(
        self,
        *app: str,
        destroy_storage: bool = False,
        force: bool = False,
    ) -> None:
        """Remove applications from the model.

        Args:
            app: Name of the application or applications to remove.
            destroy_storage: If True, also destroy storage attached to application units.
            force: Force removal even if an application is in an error state.
        """
        args = ['remove-application', '--no-prompt', *app]

        if destroy_storage:
            args.append('--destroy-storage')
        if force:
            args.append('--force')

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

    def scp(
        self,
        source: str | pathlib.Path,
        destination: str | pathlib.Path,
        *,
        container: str | None = None,
        host_key_checks: bool = True,
        scp_options: Iterable[str] = (),
    ) -> None:
        """Securely transfer files within a model.

        Args:
            source: Source of file, in format ``[[<user>@]<target>:]<path>``.
            destination: Destination for file, in format ``[<user>@]<target>[:<path>]``.
            container: Name of container for Kubernetes charms. Defaults to the charm container.
            host_key_checks: Set to False to disable host key checking (insecure).
            scp_options: ``scp`` client options, for example ``['-r', '-C']``.
        """
        # Need this check because str is also an iterable of str.
        if isinstance(scp_options, str):
            raise TypeError('scp_options must be an iterable of str, not str')

        args = ['scp']
        if container is not None:
            args.extend(['--container', container])
        if not host_key_checks:
            args.append('--no-host-key-checks')
        args.append('--')
        args.extend(scp_options)
        args.append(str(source))
        args.append(str(destination))

        self.cli(*args)

    def ssh(
        self,
        target: str | int,
        command: str,
        *args: str,
        container: str | None = None,
        host_key_checks: bool = True,
        ssh_options: Iterable[str] = (),
        user: str | None = None,
    ) -> str:
        """Executes a command using SSH on a machine or container and returns its standard output.

        Args:
            target: Where to run the command; this is a unit name such as ``mysql/0`` or a machine
                ID such as ``0``.
            command: Command to run. Because the command is executed using the shell,
                arguments may also be included here as a single string, for example
                ``juju.ssh('mysql/0', 'echo foo', ...)``.
            args: Arguments of the command.
            container: Name of container for Kubernetes charms. Defaults to the charm container.
            host_key_checks: Set to False to disable host key checking (insecure).
            ssh_options: OpenSSH client options, for example ``['-i', '/path/to/private.key']``.
            user: User account to make connection with. Defaults to ``ubuntu`` account.
        """
        # Need this check because str is also an iterable of str.
        if isinstance(ssh_options, str):
            raise TypeError('ssh_options must be an iterable of str, not str')

        cli_args = ['ssh']
        if container is not None:
            cli_args.extend(['--container', container])
        if not host_key_checks:
            cli_args.append('--no-host-key-checks')
        if user is not None:
            cli_args.append(f'{user}@{target}')
        else:
            cli_args.append(str(target))
        cli_args.extend(ssh_options)
        cli_args.append(command)
        cli_args.extend(args)

        return self.cli(*cli_args)

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
            juju.wait(jubilant.all_active)

            # Or something more complex: wait specifically for 'snappass-test' to be active,
            # and raise if any app or unit is seen in "error" status while waiting.
            juju.wait(
                lambda status: jubilant.all_active(status, 'snappass-test'),
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

            stdout, _ = self._cli('status', '--format', 'json', log=False)
            result = json.loads(stdout)
            status = Status._from_dict(result)

            if status != prev_status:
                diff = _status_diff(prev_status, status)
                if diff:
                    logger_wait.info('wait: status changed:\n%s', diff)

            if error is not None and error(status):
                raise WaitError(f'error function {error.__qualname__} returned true\n{status}')

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
    if v is None:  # type: ignore
        raise TypeError(f'unexpected None value for config key {k!r}')
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
