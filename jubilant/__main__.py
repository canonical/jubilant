"""Jubilant CLI."""

from __future__ import annotations

import argparse
import logging
import sys
import textwrap
import time
from collections.abc import Callable, Sequence
from typing import Any

import jubilant

logger = logging.getLogger('jubilant.cli')

# ISO 8601.
DATE_FORMAT = '%Y-%m-%dT%H:%M:%SZ'


# ISO 8601 requires UTC.
class _UTCFormatter(logging.Formatter):
    converter = time.gmtime


def configure_logging(verbose: bool) -> None:
    """Configure logging.

    Logs are piped to stderr. The level is set
    """
    root_logger = logging.getLogger()

    handler = logging.StreamHandler(sys.stderr)

    formatter = None
    log_level = logging.INFO
    if verbose:
        formatter = _UTCFormatter(
            fmt='%(asctime)s %(levelname)s %(name)s %(message)s',
            datefmt=DATE_FORMAT,
        )
        log_level = logging.DEBUG
    else:
        formatter = _UTCFormatter(
            fmt='%(asctime)s %(message)s',
            datefmt=DATE_FORMAT,
        )

    handler.setFormatter(formatter)
    root_logger.addHandler(handler)
    root_logger.setLevel(log_level)


def main(argv: Sequence[str] | None = None) -> int:
    """The main entrypoint."""
    arg_parser = argparse.ArgumentParser('jubilant')

    arg_parser.add_argument(
        '--verbose',
        action='store_true',
        help='Increase verbosity.',
    )

    arg_parser.add_argument(
        '--juju-cli-bin',
        default='juju',
        help='Path to the Juju CLI binary. Default: juju',
    )

    sub_parser = arg_parser.add_subparsers(dest='command')

    a: str = """
    Fetches the Juju status repeatedly (waiting `delay` seconds between)
    and wait until `ready` evaluates to True `successes` times in a row.

    If `--error` is provided and it evaluates to True, we will immediately terminate
    and returns a non zero status code.

    If `--timeout` is provided and the wait time surpass that, we will immediately
    terminate and returns a non zero status code.

    `ready` and `--error` both accept Python expression as a string. They have access to
    the jubilant module, the jubilant.Juju instance, and the jubilant.Status object.

    Example:
        juju.wait(jubilant.all_active)
        juju.wait(
            lambda status: jubilant.all_active(status, 'snappass-test'),
            error=jubilant.any_error,
        )

    can be run from the CLI as:
        jubilant wait jubilant.all_active
        jubilant wait "jubilant.all_active(status, 'snappass-test')"
    """
    wait_parser = sub_parser.add_parser(
        name='wait',
        description=textwrap.dedent(a).strip(),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    wait_parser.add_argument(
        'ready',
        help='The Python expression for the ready condition.',
    )

    wait_parser.add_argument(
        '-e',
        '--error',
        default=None,
        help='The Python expression for the error condition.',
    )

    wait_parser.add_argument(
        '-d',
        '--delay',
        type=float,
        default=1.0,
        help='Delay in seconds between status calls. Default: 1.0',
    )

    wait_parser.add_argument(
        '-t',
        '--timeout',
        type=float,
        default=180.0,
        help='Overall timeout in seconds. Default: 180.0',
    )

    wait_parser.add_argument(
        '-s',
        '--successes',
        type=int,
        default=3,
        help='Number of times `ready` must evaluate to True for the wait to succeed. Default: 3',
    )

    args = arg_parser.parse_args(argv)
    configure_logging(args.verbose)

    if args.command != 'wait':
        arg_parser.print_usage()
        return 1

    juju = jubilant.Juju(cli_binary=args.juju_cli_bin)

    def _helper(expression: str) -> Callable[[jubilant.Status], bool]:
        return lambda status, val=expression: eval(  # noqa: S307
            val,
            {'jubilant': jubilant, 'juju': juju, 'status': status},
        )

    wait_kwargs: dict[str, Any] = {
        'ready': _helper(args.ready),
        'delay': args.delay,
        'timeout': args.timeout,
        'successes': args.successes,
    }
    if args.error is not None:
        wait_kwargs['error'] = _helper(args.error)

    try:
        juju.wait(**wait_kwargs)
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
