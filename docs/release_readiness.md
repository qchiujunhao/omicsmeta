# Release Readiness

`omicsmeta` is pre-alpha. A release is ready for external users only after the
package artifacts, documentation, benchmarks, and project metadata have all been
checked from a clean checkout.

This checklist is for validation only. Publishing to PyPI, conda, Bioconda, or
the Galaxy Tool Shed requires explicit maintainer approval.

The preferred PyPI release path is GitHub Actions Trusted Publishing. Configure
a PyPI pending publisher for project `omicsmeta` with owner `qchiujunhao`,
repository `omicsmeta`, workflow `publish.yml`, and environment `pypi`; then
publish a GitHub release from the verified tag.

## Required Checks

Run the development test suite and coverage gate:

```bash
python -m pip install -e ".[dev]"
python -m pytest --cov=omicsmeta --cov-report=term-missing --cov-fail-under=70
```

Build the documentation when MkDocs is installed:

```bash
python -m pip install -e ".[docs]"
mkdocs build --strict
```

Build and validate distribution artifacts without uploading them:

```bash
python -m pip install build twine
python -m build
python -m twine check dist/*.tar.gz dist/*.whl
```

Install the generated wheel into a fresh environment and confirm that the CLI
entry point starts:

```bash
python -m pip install dist/omicsmeta-*.whl
omicsmeta --help
```

## Manual Review

- Confirm the changelog describes the unreleased user-facing changes.
- Confirm README and documentation examples still match the current CLI.
- Confirm benchmark fixtures and expected outputs represent the validation
  claims made in the documentation and paper.
- Confirm package metadata, project URLs, license, and citation text are
  accurate.
- Confirm the PyPI Trusted Publisher or pending publisher is configured before
  publishing the GitHub release.
- Confirm Galaxy wrapper validation has been completed before any Tool Shed
  submission.
