# Contributing

Thank you for considering a contribution to `omicsmeta`. The project is
pre-alpha, so the highest-value contributions are focused tests, small bug
fixes, documentation improvements, and real metadata examples with expected
outputs.

## Development Setup

```bash
python -m pip install -e ".[dev]"
python -m pytest
```

Run the coverage gate used during development:

```bash
python -m pytest --cov=omicsmeta --cov-report=term-missing --cov-fail-under=70
```

## Contribution Guidelines

- Keep changes focused. A pull request should usually address one feature,
  bug, fixture, or documentation topic.
- Add tests for new behavior, especially field detection, ontology mapping,
  validation, CLI output, and real metadata fixtures.
- Preserve provenance in outputs. New transformations should keep enough source
  context for a curator to audit the result.
- Prefer conservative defaults. Uncertain mappings should be reported for
  review instead of silently accepted.
- Public documentation should assume readers do not know any prior discussion
  about the project.

## Reporting Issues

Useful issue reports include:

- the exact command or Python snippet that failed;
- a small input file or fixture;
- expected and actual outputs;
- the installed `omicsmeta` version or commit hash;
- whether the issue involves local OBO files, managed ontology resources, or
  the optional `text2term` backend.

## Release Readiness

Before any release intended for external users, maintainers should verify that
the test suite passes, documentation examples run from a clean checkout, and the
paper and citation metadata do not overstate the validation status of the
software.

See the public [release readiness checklist](docs/release_readiness.md) for the
artifact build, documentation, benchmark, and manual review checks. The
checklist validates readiness only; publishing requires explicit maintainer
approval.
