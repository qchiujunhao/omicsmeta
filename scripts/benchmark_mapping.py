#!/usr/bin/env python3
"""Benchmark omicsmeta mappings against a known-answer TSV."""

from __future__ import annotations

import argparse
import json

from omicsmeta.benchmark import benchmark_file, write_benchmark_json


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="metadata input file")
    parser.add_argument("--truth", required=True, help="known-answer TSV")
    parser.add_argument("--input-type", choices=["tabular", "geo_soft"], default="tabular")
    parser.add_argument("--confidence-threshold", type=float, default=0.70)
    parser.add_argument("--output-json", help="optional JSON output path")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    summary = benchmark_file(
        args.input,
        args.truth,
        input_type=args.input_type,
        confidence_threshold=args.confidence_threshold,
    )
    if args.output_json:
        write_benchmark_json(summary, args.output_json)
    else:
        print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

