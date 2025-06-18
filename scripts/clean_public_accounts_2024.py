#!/usr/bin/env python3
"""
Clean Ontario Public Accounts revenue and expense data for fiscal year 2024.

• Revenue source: PublicAccountsPDFs/2024/tbs-public-accounts-annual-report-revenue-by-source-2023-24-en-fr.csv
• Expense source: PublicAccountsPDFs/2024/f4801adb-b00a-4798-9802-005231e275ee (1).json

Outputs (overwritten each run):
  clean_revenue_2024.csv   – columns: revenue_type,revenue_detail,amount_dollars
  clean_expenses_2024.csv  – flattened hierarchy with columns described below

Both outputs live in the same directory as this script (repository root level).
"""
import csv
import decimal
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # repo root
REV_PATH = ROOT / "PublicAccountsPDFs/2024/tbs-public-accounts-annual-report-revenue-by-source-2023-24-en-fr.csv"
EXP_PATH = ROOT / "PublicAccountsPDFs/2024/f4801adb-b00a-4798-9802-005231e275ee (1).json"

OUT_REV = ROOT / "clean_revenue_2024.csv"
OUT_EXP = ROOT / "clean_expenses_2024.csv"

def clean_amount(value: str, *, millions: bool) -> decimal.Decimal | None:
    """Return Decimal dollars (not millions) or None if blank/dash."""
    if value is None:
        return None
    txt = str(value).replace(",", "").strip()
    # Handle blanks, em dashes, etc.
    if txt in {"", "-", "–", "—", "- ", " - "}:  # includes nbspace dash
        return None
    try:
        amt = decimal.Decimal(txt)
        if millions:
            amt *= 1_000_000
        return amt
    except decimal.InvalidOperation:
        return None

def clean_revenue():
    rows: list[tuple[str, str, decimal.Decimal]] = []
    with REV_PATH.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        # Identify the amount column (contains 'Amount' in header)
        amount_col = next((h for h in reader.fieldnames if 'Amount' in h), None)
        if amount_col is None:
            raise RuntimeError('Could not locate amount column in revenue CSV.')
        for r in reader:
            fy = r["Year/Année"].strip()
            if fy not in {"2023-24", "23-24"} and not fy.endswith("23-24"):
                continue  # skip non-2024 years
            amt = clean_amount(r[amount_col], millions=True)
            if amt is None:
                continue
            rev_type = r["Revenue type"].strip()
            rev_detail = r["Revenue type details"].strip()
            rows.append((rev_type, rev_detail, amt))

    # write cleaned CSV
    with OUT_REV.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["revenue_type", "revenue_detail", "amount_dollars"])
        for row in rows:
            w.writerow(row)
    print(f"Wrote {len(rows)} revenue rows to {OUT_REV.relative_to(ROOT)}")

def clean_expenses():
    data = json.loads(EXP_PATH.read_text(encoding="utf-8"))
    headers = [fld["id"] for fld in data["fields"]]
    idx_year = headers.index("Year")
    idx_amt = headers.index("Amount $")

    # We'll keep the remaining columns as part of hierarchy.
    kept_cols = [
        "Ministry Name",
        "Expenditure Category (Operating / Capital)",
        "Program Name",
        "Activity / Item",
        "Sub Item",
        "Standard Account (Expense/Asset Name)",
        "Account Details (Expense/Asset Details)",
    ]
    idx_map = {col: headers.index(col) for col in kept_cols}

    cleaned_rows: list[list[str | decimal.Decimal]] = []
    for rec in data["records"]:
        fy = rec[idx_year]
        if fy != "2023-24":
            continue
        amt = clean_amount(rec[idx_amt], millions=False)
        if amt is None:
            continue
        path_vals = []
        for col in kept_cols:
            val = rec[idx_map[col]]
            if isinstance(val, str):
                val = val.strip()
                if val in {"", "No Value"}:
                    val = ""
            path_vals.append(val)
        cleaned_rows.append(path_vals + [amt])

    with OUT_EXP.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([*kept_cols, "amount_dollars"])
        w.writerows(cleaned_rows)
    print(f"Wrote {len(cleaned_rows)} expense rows to {OUT_EXP.relative_to(ROOT)}")


def main():
    clean_revenue()
    clean_expenses()

if __name__ == "__main__":
    main() 