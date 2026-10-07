#!/usr/bin/env python3
"""fuzzy_match_vendors.py - find near-duplicate vendor names in a supplier master.

Fraud and error both hide in the master file: one supplier entered three times with
slightly different spellings means split spend, missed rebates and a control gap.
This script flags candidate pairs for human review - it never merges anything.

Method (standard library only):
  1. Normalise names: uppercase, strip punctuation, singularise tokens and drop
     common legal/industry boilerplate (PVT, LTD, LIMITED, PLC, INC, CO,
     ENTERPRISE, TRADING, SUPPLIES, SERVICES, ...).
  2. Block on the first two characters of the normalised name and on the sorted
     token set's first token, so we do not compare every pair to every other pair.
  3. Score each candidate pair with token-set Jaccard similarity plus a
     difflib.SequenceMatcher ratio on the singularised names.
  4. Report pairs at or above a threshold (default 0.80) with the evidence,
     sorted by score.

Usage:
    python3 scripts/fuzzy_match_vendors.py
    python3 scripts/fuzzy_match_vendors.py --file data/raw/DimVendor.csv --threshold 0.75
    python3 scripts/fuzzy_match_vendors.py --column VendorName

Output: a ranked table on screen and data/scored/vendor_match_candidates.csv
"""

from __future__ import annotations

import argparse
import csv
import os
import re
import sys
from difflib import SequenceMatcher

DEFAULT_FILE = os.path.join("data", "raw", "DimVendor.csv")
DEFAULT_OUT = os.path.join("data", "scored", "vendor_match_candidates.csv")
DEFAULT_COLUMN = "VendorName"

SUFFIXES = {
    "PVT", "PVTLTD", "PRIVATE", "LTD", "LIMITED", "PLC", "INC", "LLC", "CO",
    "COMPANY", "CORP", "CORPORATION", "ENTERPRISE", "TRADING", "HOLDING",
    "GROUP", "INDUSTRY", "SUPPLY", "SUPPLIER", "SERVICE", "CONSULTING",
    "LOGISTIC", "ADVISORY", "GENERAL", "AND", "THE", "OF", "ZIMBABWE", "ZW",
    "AFRICA", "AFRICAN", "BROKER", "ATTORNEY", "PARTNER",
}

PUNCT = re.compile(r"[^A-Z0-9 ]+")
SPACES = re.compile(r"\s+")


def singularise(token: str) -> str:
    """Crude singular form good enough for supplier names (TUBES->TUBE, SUPPLIES->SUPPLY)."""
    if len(token) > 4 and token.endswith("IES"):
        return token[:-3] + "Y"
    if len(token) > 3 and token.endswith("S") and not token.endswith("SS"):
        return token[:-1]
    return token


def tokens(name: str, drop_suffixes: bool = True):
    """Tokenise a supplier name: upper-case, strip punctuation, singularise, optionally
    remove legal/industry boilerplate (PVT, LTD, TRADING, ...)."""
    if not name:
        return []
    text = PUNCT.sub(" ", name.upper())
    out = []
    for raw in SPACES.sub(" ", text).strip().split(" "):
        if not raw:
            continue
        token = singularise(raw)
        if drop_suffixes and (raw in SUFFIXES or token in SUFFIXES):
            continue
        out.append(token)
    out = [t for t in out if t not in SUFFIXES] if drop_suffixes else out
    if not out:                      # a name made entirely of boilerplate
        out = [tokens(name, drop_suffixes=False)[0]] if name.strip() else []
    return out


def normalise(name: str) -> str:
    """Boilerplate-free core of the supplier name - used for blocking and exact matching."""
    return " ".join(tokens(name, drop_suffixes=True))


def token_set(name: str) -> frozenset:
    return frozenset(tokens(name, drop_suffixes=True))


def score_pair(a: str, b: str) -> float:
    """Blend of token-set similarity and character-sequence similarity.

    Token-set similarity catches re-ordered and abbreviated names; the sequence
    ratio catches typos, single-letter differences and extra words."""
    ta, tb = token_set(a), token_set(b)
    if not ta or not tb:
        return 0.0
    if ta == tb:
        return 1.0
    jaccard = len(ta & tb) / len(ta | tb)
    seq = SequenceMatcher(None, " ".join(tokens(a, drop_suffixes=False)),
                          " ".join(tokens(b, drop_suffixes=False))).ratio()
    return round(0.6 * jaccard + 0.4 * seq, 4)


def load_rows(path: str, column: str):
    with open(path, newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        if column not in (reader.fieldnames or []):
            raise SystemExit(
                f"Column '{column}' not found. Available: {', '.join(reader.fieldnames or [])}"
            )
        return list(reader)


def block_key(normalised: str) -> str:
    """Cheap blocking: first two characters, and the first token."""
    first_token = normalised.split(" ")[0] if normalised else ""
    return f"{normalised[:2]}|{first_token[:4]}"


def find_candidates(rows, column, threshold):
    prepared = []
    for row in rows:
        name = (row.get(column) or "").strip()
        if not name:
            continue
        norm = normalise(name)
        prepared.append((row, name, norm, block_key(norm)))

    buckets = {}
    for item in prepared:
        buckets.setdefault(item[3], []).append(item)

    seen, out = set(), []
    for bucket in buckets.values():
        for i, (row_a, name_a, norm_a, _) in enumerate(bucket):
            for row_b, name_b, norm_b, _ in bucket[i + 1:]:
                key = tuple(sorted((row_a.get("VendorID", name_a), row_b.get("VendorID", name_b))))
                if key in seen:
                    continue
                seen.add(key)
                if norm_a == norm_b:
                    score = 1.0
                else:
                    score = score_pair(name_a, name_b)
                if score >= threshold:
                    out.append({
                        "Score": score,
                        "VendorID_A": row_a.get("VendorID", ""),
                        "VendorName_A": name_a,
                        "VendorID_B": row_b.get("VendorID", ""),
                        "VendorName_B": name_b,
                        "NormalisedA": norm_a,
                        "NormalisedB": norm_b,
                        "ExactMatchAfterNormalising": "Yes" if norm_a == norm_b else "No",
                        "ReviewConclusion": "",
                    })
    out.sort(key=lambda r: (-r["Score"], r["VendorName_A"], r["VendorName_B"]))
    return out


def main(argv=None):
    parser = argparse.ArgumentParser(description="Find near-duplicate vendor names for review.")
    parser.add_argument("--file", default=DEFAULT_FILE, help=f"vendor master CSV (default {DEFAULT_FILE})")
    parser.add_argument("--column", default=DEFAULT_COLUMN, help=f"name column (default {DEFAULT_COLUMN})")
    parser.add_argument("--threshold", type=float, default=0.80, help="minimum score to report (default 0.80)")
    parser.add_argument("--out", default=DEFAULT_OUT, help=f"output CSV (default {DEFAULT_OUT})")
    args = parser.parse_args(argv)

    if not os.path.exists(args.file):
        raise SystemExit(f"File not found: {args.file}")

    rows = load_rows(args.file, args.column)
    matches = find_candidates(rows, args.column, args.threshold)

    print(f"Vendor master: {len(rows)} records from {args.file}")
    print(f"Near-duplicate candidates at score >= {args.threshold:.2f}: {len(matches)}")
    print()
    if matches:
        print(f"{'Score':>6}  {'Vendor A':<38} {'Vendor B':<38} Exact")
        print("-" * 96)
        for m in matches[:50]:
            print(f"{m['Score']:>6.2f}  {m['VendorName_A'][:37]:<38} {m['VendorName_B'][:37]:<38} "
                  f"{m['ExactMatchAfterNormalising']}")
        if len(matches) > 50:
            print(f"  ... and {len(matches) - 50} more (see the output file)")
    else:
        print("None found. That is a good sign, but confirm against invoice addresses and bank details - "
              "a duplicate supplier can also hide behind a completely different name.")

    if matches:
        os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
        with open(args.out, "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(matches[0].keys()))
            writer.writeheader()
            writer.writerows(matches)
        print(f"\nWritten: {args.out}")
        print("Next: review each pair against invoice documents, bank account details and the "
              "approval trail. Never merge a supplier on the strength of a name match alone.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
