(security)=

# Security

When producing security documentation for your charm, it's important to consider the security aspects of the charm's tests. If there are any security questions that aren't answered here in terms of the use of cryptographic technology, security risks, hardening, and good practice, with regards to Jubilant, please reach out to the Charm Tech team, and we'll do our best to assist.

## Cryptographic technology

Jubilant does not use any cryptographic technology, hashing, or digital signatures.

## Inter-process communication

Jubilant communicates with Juju by running processes in the test environment (the Juju CLI).

> See also:
> - {external+juju:ref}`Juju CLI <list-of-juju-cli-commands>`

## Hardening

No additional steps are required to harden your integration tests when using Jubilant.

> See also: {external+juju:ref}`Juju | Harden your deployment <harden-your-deployment>`

## Security updates

We strongly recommend restricting the version of `jubilant` in `pyproject.toml` in a way that allows picking up new compatible releases every time that you re-lock. For example, `jubilant~=1.2`. Set a minor version that includes all the features that the charm tests use.

Your charm repository should have tooling configured so that any dependencies with security updates are detected automatically (such as [Dependabot](https://docs.github.com/en/code-security/dependabot/dependabot-security-updates/about-dependabot-security-updates) or [Renovate](https://www.mend.io/renovate/)), prompting to you re-lock so that the charm will be built with the latest version.

For information about supported versions and how to report security issues, see [SECURITY.md](https://github.com/canonical/jubilant/blob/main/SECURITY.md).

## Risks

Jubilant inherits the risks of using the Juju CLI. Charm authors should be familiar with {external+juju:ref}`Juju security <juju-security>`.

Charm integration tests are most commonly run in ephemeral CI environments. However, the tests may also be run in local development environments. Charm authors should be mindful of this when writing integration tests.

Otherwise, Jubilant doesn't introduce any new security risks over simply running Juju CLI commands.

## Good practices

* Where charm tests require cloud credentials, these should be saved in an appropriate secret store (such as GitHub secrets), should be used only for the integration tests, and should provide no access to production clouds.
* Only `deploy(trust=True)`, `refresh(trust=True)`, and `trust(remove=False)` in tests when required by the relevant charm, and ensure that the cloud credentials that the charm will gain access to is only used for integration tests.
* When using `scp()` use a secure temporary directory for the local side.
* Charms should follow best practices for writing secure Python tests.
* Charms should have workflows that statically check for security issues (such as [ruff](https://docs.astral.sh/ruff/linter/) and [zizmor](https://docs.zizmor.sh/)).
* Charm authors should exercise caution when considering adding dependencies to their charm tests.
* Write the exact dependencies of the charm's tests into a lock file (using `uv lock`, `poetry lock`, or similar tool) and commit that lock file to source control.
* Charm repositories should have tooling that automatically detects outdated dependencies, particularly missing security updates.
