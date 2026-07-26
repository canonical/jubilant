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


def main(argv: Sequence[str] | None = None) -> int:
    """The main entrypoint."""
    arg_parser = argparse.ArgumentParser(
        'jubilant',
    )

    group = arg_parser.add_mutually_exclusive_group()

    group.add_argument(
        '--verbose',
        action='store_true',
        help='Increase verbosity.',
    )

    group.add_argument(
        '--quiet',
        action='store_true',
        help='Suppress all output except errors.',
    )

    arg_parser.add_argument(
        '--juju-cli-bin',
        default='juju',
        help='Path to the Juju CLI binary. Default: juju',
    )

    sub_parser = arg_parser.add_subparsers(dest='command')

    # version subcommand
    _ = sub_parser.add_parser(
        name='version',
        description='Show the version.',
    )

    wait_description: str = """
    The wait command queries Juju status and checks that the ready condition succeeds
    a number of times in a row (default 3).

    Use --error to terminate the command early with a condition.

    Both ready and --error accept Python expressions. Those expressions have accesses to
    three variables: "jubilant" (the jubilant module), "juju" (the jubilant.Juju instance),
    and "status" (the jubilant.Status object).

    Examples:
        juju.wait(jubilant.all_active)
        juju.wait(
            lambda status: jubilant.all_active(status, 'snappass-test'),
            error=jubilant.any_error,
        )

    can be run from the CLI as:
        jubilant wait jubilant.all_active
        jubilant wait 'jubilant.all_active(status, "snappass-test")'
    """
    wait_parser = sub_parser.add_parser(
        name='wait',
        description=textwrap.dedent(wait_description).strip(),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    wait_parser.add_argument(
        'ready',
        help='The Python expression for the ready condition.',
    )

    wait_parser.add_argument(
        '--delay',
        type=float,
        default=1.0,
        help='Delay in seconds between status calls. (default: %(default)s)',
    )

    wait_parser.add_argument(
        '--error',
        default=None,
        help='The Python expression for the error condition. (default: %(default)s)',
    )

    wait_parser.add_argument(
        '--timeout',
        type=float,
        default=180.0,
        help='Overall timeout in seconds. (default: %(default)s)',
    )

    wait_parser.add_argument(
        '--successes',
        type=int,
        default=3,
        help=(
            'Number of times `ready` must evaluate to True for the wait to succeed. '
            '(default: %(default)s)'
        ),
    )

    args = arg_parser.parse_args(argv)

    if args.command == 'version':
        print(jubilant.__version__)
        return 0
    elif args.command != 'wait':
        arg_parser.print_usage(file=sys.stderr)
        return 1

    if args.quiet:
        configure_logging(logging.WARNING)
    elif args.verbose:
        configure_logging(logging.DEBUG)
    else:
        configure_logging(logging.INFO)

    juju = jubilant.Juju(cli_binary=args.juju_cli_bin)

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
        return 1
    except Exception as error:
        logger.error(
            'Exception evaluating "ready" or "error": %s: %s',
            type(error).__name__,
            str(error),
        )
        return 1

    logger.info('Ready condition succeeded %d times (%s)', args.successes, args.ready)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
