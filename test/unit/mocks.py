import subprocess


class Run:
    def __init__(self):
        self.commands = {}

    def handle(self, args: list[str], returncode: int = 0, stdout: str = '', stderr: str = ''):
        self.commands[tuple(args)] = (returncode, stdout, stderr)

    def __call__(
        self,
        args: list[str],
        check: bool = False,
        capture_output: bool = False,
        encoding: str | None = None,
    ) -> subprocess.CompletedProcess:
        assert check is True
        assert capture_output is True
        assert encoding == 'utf-8'
        assert tuple(args) in self.commands, f'unhandled command {args}'
        returncode, stdout, stderr = self.commands[tuple(args)]
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
