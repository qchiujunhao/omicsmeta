#!/usr/bin/env python3
"""Thin Galaxy wrapper around the omicsmeta CLI."""

from __future__ import annotations

import argparse

from omicsmeta.cli import main as omicsmeta_main


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True)
    parser.add_argument(
        "--input-type",
        choices=["tabular", "geo_soft", "biosample_xml", "sra_xml"],
        default="tabular",
    )
    parser.add_argument("--confidence-threshold", type=float, default=0.70)
    parser.add_argument("--output-harmonized", required=True)
    parser.add_argument("--output-unmapped", required=True)
    parser.add_argument("--output-unmapped-summary", required=True)
    parser.add_argument("--output-samples", required=True)
    parser.add_argument("--output-report", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return omicsmeta_main(
        [
            "harmonize",
            args.input,
            "--input-type",
            args.input_type,
            "--confidence-threshold",
            str(args.confidence_threshold),
            "--output",
            args.output_harmonized,
            "--unmapped",
            args.output_unmapped,
            "--unmapped-summary-output",
            args.output_unmapped_summary,
            "--sample-output",
            args.output_samples,
            "--report",
            args.output_report,
        ]
    )


if __name__ == "__main__":
    raise SystemExit(main())
