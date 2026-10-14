# Freelance Portfolio Sample: CSV Data Cleaner

A small, self-contained Python project that demonstrates cleaning a sales CSV for a hypothetical small business. It uses only Python's standard library; no package installation is needed.

## What it does

- Trims and normalises extra spaces in text fields.
- Normalises recognised dates to `YYYY-MM-DD`.
- Normalises valid non-negative amounts to two decimal places.
- Removes duplicate rows using normalised date, customer, product and amount.
- Preserves invalid rows separately and records why they need review.
- Produces a human-readable summary report.

## Run it

From this folder, run:

```bash
python3 clean_sales.py sample_input/raw_sales.csv --outdir output
```

Outputs:

- `output/cleaned_sales.csv`
- `output/rejected_rows.csv`
- `output/report.txt`

The `sample_input/raw_sales.csv` file contains fictional sample data only. Do not put employer or client-confidential data in a public portfolio.

## Scope and limitations

This demo expects CSV input with columns `Date`, `Customer`, `Product`, and `Amount`. It is not a universal data-cleaning engine; confirm business rules before using this approach on real client data. In particular, duplicate detection may need to be changed depending on the client's definition of a duplicate.

## Portfolio description

**Problem:** Small businesses may receive inconsistent CSV exports containing extra spaces, different date formats, repeated records and invalid amounts.

**Solution:** A Python command-line tool that standardises key fields, removes matching duplicates, saves invalid rows for review and produces a summary report.

**Possible next improvements:** Support Excel `.xlsx` input, configurable column mapping, a graphical interface, logging, automated tests and a batch-folder mode.
