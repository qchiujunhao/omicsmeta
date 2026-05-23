"""Command-line interface for omicsmeta."""

from __future__ import annotations

import argparse

from omicsmeta.core.harmonizer import Harmonizer
from omicsmeta.core.mapper import BuiltinMapper, Text2TermMapper, load_builtin_terms
from omicsmeta.io.writers import write_html_report, write_tabular


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="omicsmeta")
    subparsers = parser.add_subparsers(dest="command", required=True)

    harmonize = subparsers.add_parser("harmonize", help="harmonize metadata from a file or GEO accession")
    harmonize.add_argument("input", nargs="?", help="input metadata file")
    harmonize.add_argument("--input-type", choices=["tabular", "geo_soft"], default="tabular")
    harmonize.add_argument("--geo-accession", help="GEO accession to fetch directly, such as GSE123456")
    harmonize.add_argument("--output", required=True, help="harmonized output TSV")
    harmonize.add_argument("--unmapped", required=True, help="unmapped terms TSV")
    harmonize.add_argument("--report", required=True, help="HTML QC report")
    harmonize.add_argument("--confidence-threshold", type=float, default=0.70)
    harmonize.add_argument("--mapper", choices=["builtin", "text2term"], default="builtin")
    harmonize.add_argument(
        "--ontology-obo",
        action="append",
        default=[],
        help="local OBO file to load into the built-in mapper; may be repeated",
    )
    harmonize.add_argument(
        "--no-default-terms",
        action="store_true",
        help="use only terms loaded from --ontology-obo with the built-in mapper",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "harmonize":
        if not args.input and not args.geo_accession:
            parser.error("harmonize requires an input file or --geo-accession")

        mapper = _mapper(
            args.mapper,
            args.confidence_threshold,
            ontology_paths=args.ontology_obo,
            include_defaults=not args.no_default_terms,
        )
        harmonizer = Harmonizer(mapper=mapper, confidence_threshold=args.confidence_threshold)
        if args.geo_accession:
            result = harmonizer.from_geo(args.geo_accession)
        else:
            result = harmonizer.from_file(args.input, file_type=args.input_type)
        write_tabular(result.harmonized, args.output)
        write_tabular(result.unmapped, args.unmapped)
        write_html_report(result.qc_summary, args.report)
        return 0

    parser.error(f"Unhandled command: {args.command}")
    return 2


def _mapper(
    name: str,
    confidence_threshold: float,
    *,
    ontology_paths: list[str],
    include_defaults: bool,
) -> BuiltinMapper | Text2TermMapper:
    if name == "builtin":
        terms = load_builtin_terms(ontology_paths, include_defaults=include_defaults)
        return BuiltinMapper(terms=terms, confidence_threshold=confidence_threshold)
    if name == "text2term":
        if ontology_paths or not include_defaults:
            raise ValueError("--ontology-obo and --no-default-terms are only supported by --mapper builtin")
        return Text2TermMapper(confidence_threshold=confidence_threshold)
    raise ValueError(f"Unsupported mapper: {name}")


if __name__ == "__main__":
    raise SystemExit(main())
