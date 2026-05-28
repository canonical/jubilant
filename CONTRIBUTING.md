# Contributing and developing

Anyone can contribute to Jubilant. It's best to start by [opening an issue](https://github.com/canonical/jubilant/issues) with a clear description of the problem or feature request, but you can also [open a pull request](https://github.com/canonical/jubilant/pulls) directly.

Jubilant uses [`uv`](https://docs.astral.sh/uv/) to manage Python dependencies and tools, so you'll need to [install uv](https://docs.astral.sh/uv/#installation) to work on the library. You'll also need `make` to run local development tasks (but you probably have `make` installed already).

After that, clone the Jubilant codebase and use `make all` to run various checks and the unit tests:

```
$ git clone https://github.com/canonical/jubilant
Cloning into 'jubilant'...
...
$ cd jubilant
$ make all
...
========== 107 passed in 0.26s ==========
```

To contribute a code change, write your fix or feature, add tests and docs, then run `make all` before you push and create a PR. Once you create a PR, GitHub will also run the integration tests, which takes several minutes.


## Doing a release

To create a new release of Jubilant:

1. Create a pre-release PR:
   1. Update the `__version__` field in [`jubilant/__init__.py`](https://github.com/canonical/jubilant/blob/main/jubilant/__init__.py) to the new version.
   2. Add a changelog entry to [`CHANGES.md`](https://github.com/canonical/jubilant/blob/main/CHANGES.md) for the new version.
   3. Put the release notes in the PR description for review.
   4. Get the PR reviewed and merged.
2. Create the release:
   1. Create a [new release](https://github.com/canonical/jubilant/releases/new) on GitHub. The tag should start with a `v`, like `v1.2.3`.
   2. In the release notes, drop the `by @author` credit for anyone in the Charm Tech team (including Copilot and other AI users), and drop dependabot PRs entirely.
   3. Sort the PRs by type: breaking changes first, then feat, fix, docs, chore, ci.
   4. Publishing the release triggers the [`publish.yaml` workflow](https://github.com/canonical/jubilant/blob/main/.github/workflows/publish.yaml), which automatically publishes the package to PyPI and runs the SBOM and security scan workflow.
3. Once the Publish workflow finishes:
   1. On the summary page of the workflow run, locate the `secscan-report-upload` artifact. Download it and upload it to the [SSDLC Jubilant folder in Drive](https://drive.google.com/drive/folders/1bLJL4wJwicxaGY2hc5Xz4vSjENUt5Zjw?usp=share_link). Open the report and verify that the security scan has not found any vulnerabilities.
   2. Check that the new version appears in the [PyPI version history](https://pypi.org/project/jubilant/#history).
