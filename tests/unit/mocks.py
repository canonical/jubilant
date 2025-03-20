import dataclasses
import subprocess


@dataclasses.dataclass(frozen=True)
class Call:
    args: tuple[str, ...]
    returncode: int
    stdout: str
    stderr: str


class Run:
    """Mock for subprocess.run.

    When subprocess.run is called, the mock returns a subprocess.CompletedProcess
    instance with data passed to :meth:`handle` for those command-line arguments.
    Or, if returncode is nonzero, it raises a subprocess.CalledProcessError.

    This also asserts that the correct keyword args are passed to subprocess.run,
    for example check=True.
    """

    def __init__(self):
        self._commands: dict[tuple[str, ...], tuple[int, str, str]] = {}
        self.calls: list[Call] = []

    def handle(self, args: list[str], *, returncode: int = 0, stdout: str = '', stderr: str = ''):
        """Handle specified command-line args with the given return code, stdout, and stderr."""
        self._commands[tuple(args)] = (returncode, stdout, stderr)

    def __call__(
        self,
        args: list[str],
        check: bool = False,
        capture_output: bool = False,
        encoding: str | None = None,
    ) -> subprocess.CompletedProcess[str]:
        args_tuple = tuple(args)
        assert check is True
        assert capture_output is True
        assert encoding == 'utf-8'
        assert args_tuple in self._commands, f'unhandled command {args}'

        returncode, stdout, stderr = self._commands[args_tuple]
        self.calls.append(Call(args_tuple, returncode, stdout, stderr))
        if returncode != 0:
            raise subprocess.CalledProcessError(
                returncode=returncode,
                cmd=args,
                output=stdout,
                stderr=stderr,
            )
        return subprocess.CompletedProcess(
            args=args,
            returncode=returncode,
            stdout=stdout,
            stderr=stderr,
        )


class Time:
    """Mock for time.monotonic and time.sleep.

    This is very simplistic: time.monotonic() starts out at 0, and every time
    time.sleep(x) is called, it increases by x.
    """

    def __init__(self):
        self._monotonic = 0

    def monotonic(self) -> float:
        return self._monotonic

    def sleep(self, seconds: float):
        self._monotonic += seconds
