"""Command-line interface for omicsmeta."""

from __future__ import annotations

import argparse
from pathlib import Path

from omicsmeta.core.harmonizer import Harmonizer
from omicsmeta.core.mapper import BuiltinMapper, Text2TermMapper, load_builtin_terms
from omicsmeta.io.writers import write_html_report, write_tabular
from omicsmeta.ontologies.resources import (
    DEFAULT_CACHE_DIR,
    all_resource_names,
    build_ontology_index,
    cached_resource_paths,
    default_index_path,
    download_resources,
    resource_status,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="omicsmeta")
    subparsers = parser.add_subparsers(dest="command", required=True)

    harmonize = subparsers.add_parser("harmonize", help="harmonize metadata from a file or GEO accession")
    harmonize.add_argument("input", nargs="?", help="input metadata file")
    harmonize.add_argument("--input-type", choices=["tabular", "geo_soft"], default="tabular")
    harmonize.add_argument("--geo-accession", help="GEO accession to fetch directly, such as GSE123456")
    harmonize.add_argument("--output", required=True, help="harmonized output TSV")
    harmonize.add_argument("--unmapped", required=True, help="unmapped terms TSV")
    harmonize.add_argument("--sample-output", help="sample-wide output TSV with one row per input sample")
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
    harmonize.add_argument(
        "--ontology-resource",
        action="append",
        choices=[*all_resource_names(), "all"],
        default=[],
        help="cached managed ontology resource to load into the built-in mapper; may be repeated",
    )
    harmonize.add_argument(
        "--ontology-cache-dir",
        default=str(DEFAULT_CACHE_DIR),
        help="directory containing managed ontology resources",
    )

    ontologies = subparsers.add_parser("ontologies", help="manage local ontology resources")
    ontology_subparsers = ontologies.add_subparsers(dest="ontology_command", required=True)

    list_cmd = ontology_subparsers.add_parser("list", help="list known ontology resources")
    list_cmd.add_argument("--cache-dir", default=str(DEFAULT_CACHE_DIR))

    download_cmd = ontology_subparsers.add_parser("download", help="download ontology resources")
    download_cmd.add_argument("resources", nargs="*", choices=[*all_resource_names(), "all"])
    download_cmd.add_argument("--cache-dir", default=str(DEFAULT_CACHE_DIR))
    download_cmd.add_argument("--overwrite", action="store_true")

    index_cmd = ontology_subparsers.add_parser("index", help="build a SQLite synonym index")
    index_cmd.add_argument("--resource", action="append", choices=[*all_resource_names(), "all"], default=[])
    index_cmd.add_argument("--ontology-obo", action="append", default=[])
    index_cmd.add_argument("--cache-dir", default=str(DEFAULT_CACHE_DIR))
    index_cmd.add_argument("--output", help="SQLite output path")

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
            ontology_resources=args.ontology_resource,
            ontology_cache_dir=args.ontology_cache_dir,
            include_defaults=not args.no_default_terms,
        )
        harmonizer = Harmonizer(mapper=mapper, confidence_threshold=args.confidence_threshold)
        if args.geo_accession:
            result = harmonizer.from_geo(args.geo_accession)
        else:
            result = harmonizer.from_file(args.input, file_type=args.input_type)
        write_tabular(result.harmonized, args.output)
        write_tabular(result.unmapped, args.unmapped)
        if args.sample_output:
            write_tabular(
                result.sample_table,
                args.sample_output,
                default_columns=["row_index", "sample_id"],
            )
        write_html_report(result.qc_summary, args.report)
        return 0

    if args.command == "ontologies":
        if args.ontology_command == "list":
            _print_resource_status(args.cache_dir)
            return 0
        if args.ontology_command == "download":
            names = _expand_resource_names(args.resources or ["all"])
            paths = download_resources(names, cache_dir=args.cache_dir, overwrite=args.overwrite)
            for path in paths:
                print(path)
            return 0
        if args.ontology_command == "index":
            names = _expand_resource_names(args.resource)
            ontology_paths = []
            if names:
                ontology_paths.extend(cached_resource_paths(names, cache_dir=args.cache_dir))
            ontology_paths.extend(Path(path) for path in args.ontology_obo)
            if not ontology_paths:
                parser.error("ontologies index requires --resource or --ontology-obo")
            output = Path(args.output) if args.output else default_index_path(args.cache_dir)
            output.parent.mkdir(parents=True, exist_ok=True)
            count = build_ontology_index(ontology_paths, output_path=output)
            print(f"Indexed {count} terms into {output}")
            return 0

    parser.error(f"Unhandled command: {args.command}")
    return 2


def _mapper(
    name: str,
    confidence_threshold: float,
    *,
    ontology_paths: list[str],
    ontology_resources: list[str],
    ontology_cache_dir: str,
    include_defaults: bool,
) -> BuiltinMapper | Text2TermMapper:
    if name == "builtin":
        resource_names = _expand_resource_names(ontology_resources)
        resource_paths = cached_resource_paths(resource_names, cache_dir=ontology_cache_dir) if resource_names else []
        terms = load_builtin_terms([*resource_paths, *ontology_paths], include_defaults=include_defaults)
        return BuiltinMapper(terms=terms, confidence_threshold=confidence_threshold)
    if name == "text2term":
        if ontology_paths or ontology_resources or not include_defaults:
            raise ValueError(
                "--ontology-obo, --ontology-resource, and --no-default-terms are only supported by --mapper builtin"
            )
        return Text2TermMapper(confidence_threshold=confidence_threshold)
    raise ValueError(f"Unsupported mapper: {name}")


def _expand_resource_names(names: list[str]) -> list[str]:
    if not names:
        return []
    if "all" in names:
        return all_resource_names()
    return names


def _print_resource_status(cache_dir: str) -> None:
    print("name\tcached\tsize_bytes\tpath\turl\tdescription")
    for row in resource_status(cache_dir):
        print(
            "\t".join(
                [
                    str(row["name"]),
                    str(row["cached"]).lower(),
                    str(row["size_bytes"]),
                    str(row["path"]),
                    str(row["url"]),
                    str(row["description"]),
                ]
            )
        )


if __name__ == "__main__":
    raise SystemExit(main())
