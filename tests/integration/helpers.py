from __future__ import annotations

import pathlib

from cryptography.hazmat import backends
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

CHARMS_PATH = pathlib.Path(__file__).parent / 'charms'


def generate_ssh_key_pair() -> tuple[str, str]:
    """Generate an SSH key pair dynamically using cryptography library.

    Returns:
        Tuple of (private_key_pem, public_key_ssh) where:
        - private_key_pem is the RSA private key in PEM format
        - public_key_ssh is the public key in SSH format (ssh-rsa ...)
    """
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=backends.default_backend(),
    )
    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode()
    public_key = private_key.public_key()
    public_key_ssh = public_key.public_bytes(
        encoding=serialization.Encoding.OpenSSH,
        format=serialization.PublicFormat.OpenSSH,
    ).decode()
    return private_key_pem, public_key_ssh


def find_charm(name: str) -> pathlib.Path:
    """Find given test charm and return absolute path to .charm file."""
    # .charm filename has platform in it, so search with *.charm
    charms = [p.absolute() for p in (CHARMS_PATH / name).glob('*.charm')]
    assert charms, f'{name} .charm file not found'
    assert len(charms) == 1, f'{name} has more than one .charm file, unsure which to use'
    return charms[0]
