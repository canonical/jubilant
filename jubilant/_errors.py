import subprocess


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
    """Raised when :meth:`Juju.wait` returns false."""

    # TODO: want a "status" or other attributes?
