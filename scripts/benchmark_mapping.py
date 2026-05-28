#!/usr/bin/env python3
"""Benchmark omicsmeta mappings against a known-answer TSV."""

from __future__ import annotations

import argparse
import json

from omicsmeta.benchmark import benchmark_file, benchmark_suite, write_benchmark_json


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--input", help="metadata input file")
    source.add_argument("--manifest", help="TSV manifest of benchmark cases")
    parser.add_argument("--truth", help="known-answer TSV; required with --input")
    parser.add_argument("--input-type", choices=["tabular", "geo_soft", "biosample_xml", "sra_xml"], default="tabular")
    parser.add_argument("--confidence-threshold", type=float, default=0.70)
    parser.add_argument("--output-json", help="optional JSON output path")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.input:
        if not args.truth:
            parser.error("--truth is required with --input")
        summary = benchmark_file(
            args.input,
            args.truth,
            input_type=args.input_type,
            confidence_threshold=args.confidence_threshold,
        )
    else:
        summary = benchmark_suite(
            args.manifest,
            confidence_threshold=args.confidence_threshold,
        )
    if args.output_json:
        write_benchmark_json(summary, args.output_json)
    else:
        print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
