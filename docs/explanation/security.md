---
myst:
  html_meta:
    description: Security documentation for Jubilant — product architecture, secure by design, cryptography, hardening, logging, decommissioning, security lifecycle, and vulnerability reporting.
---

(security)=

# Security

When producing security documentation for your charm, it's important to consider the security aspects of the charm's tests. If you have any Jubilant-related security questions that aren't answered here, please reach out to the Charm Tech team, and we'll do our best to help.

## Product architecture

Jubilant is a pure-Python library with no persistent state, no network sockets, and no privileged access of its own. Its trust boundary is narrow:

```
test process → jubilant → Juju CLI subprocess → Juju controller
```

- The **test process** calls Jubilant's Python API.
- Jubilant translates each call into one or more {external+juju:ref}`Juju CLI <juju-cli>` invocations via `subprocess`. It does not communicate with Juju or any other service directly over a network.
- The **Juju CLI** handles all communication with the Juju controller, including authentication, credential management, and TLS. Jubilant never stores credentials or reads credentials from Juju.

Several Jubilant operations pass structured data to the Juju CLI by writing temporary files. For example, YAML config passed to `add_cloud()`, `add_credential()`, `add_secret()`, `run()`, and `deploy()`. When the Juju CLI is installed as a snap, these files are written to `~/snap/juju/common/` so the snap can access them; otherwise the system temporary directory is used. In both cases the files are removed immediately after the CLI call returns. This means sensitive values such as cloud credentials and secret content are never passed as command-line arguments, so they do not appear in process listings, shell history, or Jubilant's debug logs. Jubilant retains no state between test runs.

## Secure by design

Jubilant was deliberately designed as a thin wrapper over the Juju CLI rather than a reimplementation of Juju's protocol. This design choice is a security property: all authentication, credential handling, and network communication is delegated to the Juju CLI, which is independently maintained and audited. Jubilant adds no new network attack surface.

The library does not introduce any new security risks beyond directly running Juju CLI commands. Charm integration tests are most commonly run in ephemeral CI environments. When run in local development environments, Jubilant inherits whatever access the Juju CLI has to that environment — no more.

> See also: {external+juju:ref}`Juju security <juju-security>`

## Cryptographic technology

Jubilant does not use any cryptographic technology, hashing, or digital signatures. All cryptographic operations (TLS, credential storage, API authentication) are handled by the Juju CLI and the Juju controller.

## Configuring and operating

### Hardening guidelines

No additional steps are required to harden your integration tests when using Jubilant. Follow the same security and hardening practices as you would if calling the Juju CLI directly.

> See also: [Good practices](#good-practices), {external+juju:ref}`Juju | Harden your deployment <harden-your-deployment>`

### Logging and monitoring

Jubilant uses Python's standard `logging` module. No security events are logged by Jubilant itself — authentication, authorisation, and access control events are logged by the Juju CLI and the Juju controller, not by the test library.

To capture Jubilant's own log output (command invocations, return codes, and `stderr`), configure a handler for the `jubilant` logger in your test suite:

```python
import logging
logging.getLogger("jubilant").setLevel(logging.DEBUG)
```

For security-relevant events (login failures, credential errors, controller access), consult the Juju controller logs and the Juju CLI's own output rather than Jubilant's logs.

Secret and credential values are written to temporary files rather than CLI arguments, so they do not appear in Jubilant's logs. The exception is `CLIError`, raised on a Juju CLI failure: its traceback includes the CLI's `stdout` and `stderr`, so any value the Juju CLI itself echoes there would be exposed.

## Decommissioning

Removing Jubilant from a project requires no special decommissioning steps. Remove `jubilant` from your `pyproject.toml` and re-lock dependencies. Jubilant stores no credentials, configuration, or logs of its own. Any Juju environments provisioned during testing should be destroyed using the Juju CLI (`juju destroy-controller`, `juju destroy-model`) independently of removing Jubilant.

## Security lifecycle

Jubilant follows [semantic versioning](https://semver.org/). Security updates are released as patch releases on all major versions that have had releases in the last year. See [SECURITY.md](https://github.com/canonical/jubilant/blob/main/SECURITY.md) for the supported-versions policy.

**Receiving security updates.** Restrict the version of `jubilant` in `pyproject.toml` in a way that allows picking up new compatible releases every time that you re-lock dependencies. For example, `jubilant~=1.2` allows upgrades to 1.3, 1.4, and so on, while staying on the 1.x line.

**Detecting available updates.** Configure Dependabot or Renovate in your charm repository so that security updates are surfaced automatically as pull requests. Re-lock dependencies when prompted so that the charm tests run with the latest version.

**Verifying an update.** Security releases are announced via [GitHub Security Advisories](https://github.com/canonical/jubilant/security/advisories) and as GitHub release notes. Verify that the installed version matches a published release by running `pip show jubilant` or `uv pip show jubilant` in the test environment.

## Reporting vulnerabilities

Report security issues via [GitHub's security advisory for this project](https://github.com/canonical/jubilant/security/advisories/new). See [Privately reporting a security vulnerability](https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-writing/privately-reporting-a-security-vulnerability) for instructions.

You may also send email to security@ubuntu.com. If you want to encrypt your email, follow [Canonical's reporting instructions](https://ubuntu.com/security/disclosure-policy#contact-us).

Known vulnerabilities and past advisories are listed at [github.com/canonical/jubilant/security/advisories](https://github.com/canonical/jubilant/security/advisories).

The [Ubuntu Security disclosure and embargo policy](https://ubuntu.com/security/disclosure-policy) contains more information about what you can expect when you contact us, and what we expect from you.

(good-practices)=
## Good practices

* Where charm tests require cloud credentials, these should be saved in an appropriate secret store (such as GitHub secrets), should be used only for the integration tests, and should provide no access to production clouds.
* Only use `deploy(trust=True)`, `refresh(trust=True)`, and `trust(remove=False)` in tests when required by the relevant charm. Ensure that the cloud credentials that the charm will gain access to are only used for integration tests.
* When using `scp()` use a secure temporary directory for the local side.
* Avoid passing secrets or credentials as arguments to `cli()`. Arguments to `cli()` appear in Jubilant's debug log and in process listings — prefer the typed methods (such as `add_secret()` and `add_credential()`) that pass sensitive data via temporary files.
* Do not pass sensitive data as values to `config()`. Config values are sent to the Juju CLI as arguments, so they may appear in Jubilant's debug log and in process listings. Use a Juju secret instead and reference it from config.
* Charms should have workflows that statically check for security issues (such as [ruff](https://docs.astral.sh/ruff/linter/) and [zizmor](https://docs.zizmor.sh/)).
* Charms should follow best practices for writing secure Python tests.
* Charm tests may be run in local development environments, so charm tests should not install software or make system changes.
* Charm authors should exercise caution when considering adding dependencies to their charm tests.
* Write the exact dependencies of the charm's tests into a lock file (using `uv lock`, `poetry lock`, or similar tool) and commit that lock file to source control.
