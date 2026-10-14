#!/usr/bin/env python3
"""Clean a sample sales CSV using only Python's standard library.

Usage:
    python3 clean_sales.py sample_input/raw_sales.csv --outdir output

Expected columns (case-insensitive): Date, Customer, Product, Amount
Outputs:
    cleaned_sales.csv  - validated and deduplicated records
    rejected_rows.csv - records that need human review
    report.txt        - summary of the run
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Optional

REQUIRED_COLUMNS = ("date", "customer", "product", "amount")
DATE_FORMATS = ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%d.%m.%Y")


def normalise_date(value: str) -> Optional[str]:
    value = value.strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(value, fmt).date().isoformat()
        except ValueError:
            continue
    return None


def normalise_amount(value: str) -> Optional[str]:
    cleaned = value.strip().replace(",", "").replace("₹", "").replace("INR", "")
    cleaned = cleaned.strip()
    if not cleaned:
        return None
    try:
        amount = Decimal(cleaned)
    except InvalidOperation:
        return None
    if not amount.is_finite() or amount < 0:
        return None
    return f"{amount:.2f}"


def find_column(headers: list[str], name: str) -> Optional[str]:
    for header in headers:
        if header.strip().lower() == name:
            return header
    return None


def clean_file(input_path: Path, outdir: Path) -> int:
    if not input_path.exists() or not input_path.is_file():
        raise FileNotFoundError(f"Input CSV not found: {input_path}")
    outdir.mkdir(parents=True, exist_ok=True)

    with input_path.open("r", newline="", encoding="utf-8-sig") as infile:
        reader = csv.DictReader(infile)
        if not reader.fieldnames:
            raise ValueError("The input CSV appears to be empty or has no header row.")
        headers = list(reader.fieldnames)
        columns = {name: find_column(headers, name) for name in REQUIRED_COLUMNS}
        missing = [name for name, col in columns.items() if col is None]
        if missing:
            raise ValueError(
                "Missing required column(s): " + ", ".join(missing)
                + ". Expected columns: Date, Customer, Product, Amount."
            )

        cleaned_rows: list[dict[str, str]] = []
        rejected_rows: list[dict[str, str]] = []
        seen: set[tuple[str, str, str, str]] = set()
        duplicate_count = 0
        invalid_count = 0
        total_rows = 0

        for line_number, original in enumerate(reader, start=2):
            total_rows += 1
            row = {str(k): (v or "").strip() for k, v in original.items() if k is not None}
            reason = ""

            date_value = normalise_date(row.get(columns["date"] or "", ""))
            customer = " ".join(row.get(columns["customer"] or "", "").split())
            product = " ".join(row.get(columns["product"] or "", "").split())
            amount = normalise_amount(row.get(columns["amount"] or "", ""))

            if not date_value:
                reason = "Invalid or missing date"
            elif not customer:
                reason = "Missing customer"
            elif not product:
                reason = "Missing product"
            elif amount is None:
                reason = "Invalid or missing amount"

            if reason:
                invalid_count += 1
                rejected = dict(row)
                rejected["_row_number"] = str(line_number)
                rejected["_reason"] = reason
                rejected_rows.append(rejected)
                continue

            key = (date_value, customer.casefold(), product.casefold(), amount)
            if key in seen:
                duplicate_count += 1
                continue
            seen.add(key)

            output_row = dict(row)
            output_row[columns["date"] or "Date"] = date_value
            output_row[columns["customer"] or "Customer"] = customer
            output_row[columns["product"] or "Product"] = product
            output_row[columns["amount"] or "Amount"] = amount
            cleaned_rows.append(output_row)

    output_columns = headers
    cleaned_path = outdir / "cleaned_sales.csv"
    rejected_path = outdir / "rejected_rows.csv"
    report_path = outdir / "report.txt"

    with cleaned_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=output_columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(cleaned_rows)

    rejected_columns = headers + ["_row_number", "_reason"]
    with rejected_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rejected_columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rejected_rows)

    report = (
        "CSV CLEANING REPORT\n"
        "===================\n"
        f"Input file: {input_path.name}\n"
        f"Rows processed (excluding header): {total_rows}\n"
        f"Clean records written: {len(cleaned_rows)}\n"
        f"Duplicate records removed: {duplicate_count}\n"
        f"Rejected records needing review: {invalid_count}\n"
        "\nNotes:\n"
        "- Dates were normalised to YYYY-MM-DD where recognised.\n"
        "- Amounts were normalised to two decimal places.\n"
        "- Rejected rows were preserved separately with a reason.\n"
        "- Duplicate detection uses normalised date, customer, product and amount.\n"
    )
    report_path.write_text(report, encoding="utf-8")
    print(report)
    print(f"Outputs saved in: {outdir.resolve()}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Clean and validate a CSV sales file.")
    parser.add_argument("input_csv", type=Path, help="Path to the source CSV file")
    parser.add_argument("--outdir", type=Path, default=Path("output"), help="Output folder (default: output)")
    args = parser.parse_args()
    try:
        return clean_file(args.input_csv, args.outdir)
    except (OSError, ValueError, csv.Error) as exc:
        parser.error(str(exc))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
