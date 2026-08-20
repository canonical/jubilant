"""Jubilant CLI."""

from __future__ import annotations

import argparse
import logging
import sys
import textwrap
from collections.abc import Callable, Sequence

import jubilant

logger = logging.getLogger('jubilant.cli')


def configure_logging(level: int) -> None:
    """Configure logging.

    Logs are piped to stderr.
    """
    root_logger = logging.getLogger()

    handler = logging.StreamHandler(sys.stderr)

    if level <= logging.DEBUG:
        formatter = logging.Formatter(
            fmt='%(asctime)s %(levelname)s %(name)s %(message)s',
        )
    else:
        formatter = logging.Formatter(
            fmt='%(asctime)s %(message)s',
        )

    handler.setFormatter(formatter)
    root_logger.addHandler(handler)
    root_logger.setLevel(level)


def _add_verbosity_args(subparser: argparse.ArgumentParser) -> None:
    verbosity_group = subparser.add_mutually_exclusive_group()
    verbosity_group.add_argument(
        '--quiet',
        action='store_true',
        help='suppress all output except errors',
    )
    verbosity_group.add_argument(
        '--verbose',
        action='store_true',
        help='increase verbosity',
    )


def _add_juju_args(subparser: argparse.ArgumentParser) -> None:
    subparser.add_argument(
        '--juju-cli-bin',
        help='path to the Juju CLI binary',
    )
    subparser.add_argument(
        '--model',
        help='the Juju model to operate on, otherwise use the current Juju model',
    )


def main(argv: Sequence[str] | None = None) -> int:
    """The main entrypoint."""
    arg_parser = argparse.ArgumentParser(
        'jubilant',
    )

    cmd_subparsers = arg_parser.add_subparsers(dest='command', required=True)
    cmd_subparsers.add_parser(
        name='version',
        description='show the version and exit',
    )
    wait_description: str = """
    The wait command queries Juju status and checks that the ready condition succeeds
    a number of times in a row (default 3).

    Both ready and --error accept Python expressions. Those expressions have access to
    three variables: "jubilant" (the jubilant module), "juju" (the jubilant.Juju instance),
    and "status" (the jubilant.Status object).

    Examples:

        jubilant wait 'jubilant.all_active(status)'

        jubilant wait 'jubilant.all_active(status, "app")' --error 'jubilant.any_error(status)'

    These are equivalent to the following Python calls:

        juju.wait(jubilant.all_active)

        juju.wait(
            lambda status: jubilant.all_active(status, 'app'),
            error=jubilant.any_error,
        )
    """
    wait_parser = cmd_subparsers.add_parser(
        name='wait',
        description=textwrap.dedent(wait_description).strip(),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    wait_parser.add_argument(
        'ready',
        help='Python expression for the ready condition',
    )
    wait_parser.add_argument(
        '--delay',
        type=float,
        default=1.0,
        help='delay in seconds between status calls (default: %(default)s)',
    )
    wait_parser.add_argument(
        '--error',
        default=None,
        help='Python expression for the error condition (default: %(default)s)',
    )
    wait_parser.add_argument(
        '--successes',
        type=int,
        default=3,
        help=(
            'number of times `ready` must evaluate to true for the wait to succeed '
            '(default: %(default)s)'
        ),
    )
    wait_parser.add_argument(
        '--timeout',
        type=float,
        default=180.0,
        help='overall timeout in seconds (default: %(default)s)',
    )
    _add_juju_args(wait_parser)
    _add_verbosity_args(wait_parser)

    args = arg_parser.parse_args(argv)

    if args.command == 'version':
        print(jubilant.__version__)
        return 0

    if args.quiet:
        configure_logging(logging.WARNING)
    elif args.verbose:
        configure_logging(logging.DEBUG)
    else:
        configure_logging(logging.INFO)

    juju = jubilant.Juju(cli_binary=args.juju_cli_bin, model=args.model)

    # The global namespace passed into eval is meant to communicate with users
    # about what they can depend on, rather than security concerns.
    # We expect users not to rely on other built-in modules (e.g. os).
    #
    # We could go further and plug the `__builtins__` hole, to avoid:
    #   eval("__builtins__['__import__']('os').system('ls')", {}, {})
    #
    # However, we agreed that this is not an issue.
    #     - Python is very hard to sandbox
    #     - Users are unlikely to go with this approach.
    def _helper(expression: str) -> Callable[[jubilant.Status], bool]:
        return lambda status: eval(  # noqa: S307
            expression,
            {'jubilant': jubilant, 'juju': juju, 'status': status},
        )

    try:
        juju.wait(
            ready=_helper(args.ready),
            error=_helper(args.error) if args.error else None,
            delay=args.delay,
            timeout=args.timeout,
            successes=args.successes,
        )
    except jubilant.WaitError:
        logger.error('Error expression evaluated to true (%s)', args.error)
        return 1
    except TimeoutError:
        logger.error('Wait timed out after %s seconds', args.timeout)
        return 124  # The same exit code coreutils timeout uses.
    except KeyboardInterrupt:
        logger.error('Keyboard interrupt received while waiting')
        return 130  # The same exit code Python uses by default.
    except Exception as error:
        logger.error('Exception while waiting: %r', error)
        return 1

    logger.info('Ready condition succeeded %d times (%s)', args.successes, args.ready)
    return 0


if __name__ == '__main__':  # pragma: no cover
    raise SystemExit(main())
