<section class="hero">
  <div class="hero__content">
    <p class="eyebrow">Public omics metadata harmonization</p>
    <h1>omicsmeta</h1>
    <p class="hero__lede">
      Harmonize public omics metadata from GEO, SRA, BioSample, and tabular
      exports with domain-specific normalization, ontology mapping, and
      reviewable output tables.
    </p>
    <p class="hero__actions">
      <a class="md-button md-button--primary" href="quickstart/">Start with the CLI</a>
      <a class="md-button" href="design/">Read the design</a>
    </p>
  </div>
</section>

## Current Scope

The package is currently pre-alpha. The documentation describes implemented
behavior and calls out limitations where the roadmap is not complete.

<div class="feature-grid">
  <a class="feature-card" href="quickstart/">
    <strong>Run metadata harmonization</strong>
    <span>Install from PyPI, harmonize local files, and export mapped and unmapped review tables.</span>
  </a>
  <a class="feature-card" href="api/">
    <strong>Use the Python API</strong>
    <span>Call the harmonizer directly from scripts and notebooks with row dictionaries.</span>
  </a>
  <a class="feature-card" href="design/">
    <strong>Inspect pipeline decisions</strong>
    <span>Understand field detection, mapper routing, validation, and output semantics.</span>
  </a>
  <a class="feature-card" href="tutorials/basic_fixture/">
    <strong>Benchmark known answers</strong>
    <span>Run the bundled fixture and compare observed mappings to expected ontology IDs.</span>
  </a>
</div>

## Start Here

- [Quickstart](quickstart.md): install the package and run the CLI.
- [API reference](api.md): call the harmonizer from Python.
- [Design](design.md): understand pipeline decisions and output semantics.
- [Release readiness](release_readiness.md): validate artifacts and release
  claims before publishing.
- [Basic fixture tutorial](tutorials/basic_fixture.md): run the local example
  and benchmark it against known-answer mappings.
