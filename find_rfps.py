"""Find new federal RFPs on SAM.gov and SBIR/STTR sources, with the attachments already read.

Runs the "SAM.gov & SBIR Federal RFP + Attachment Deep-Parser" Actor on Apify and saves a CSV you
can sort and filter in Excel or Google Sheets.

    export APIFY_TOKEN=...   # free account: https://console.apify.com/settings/integrations
    python find_rfps.py --keywords "machine learning" "sensor fusion" --days 7 --csv rfps.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys

from apify_client import ApifyClient

ACTOR_ID = "aimindteams/govcon-rfp-deep-parser"
CLEARED = {"Confidential", "Secret", "Top Secret", "TS/SCI", "TS/SCI with Poly"}

COLUMNS = [
    "response_deadline", "title", "agency", "notice_type", "set_aside", "clearance_level",
    "evaluation_type", "page_limits", "compliance", "incumbents", "contract_numbers",
    "submit_via", "contacts", "solicitation_number", "url",
]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Find SAM.gov and SBIR/STTR opportunities and read their attachments.")
    p.add_argument("--keywords", nargs="+", default=["artificial intelligence"], help="One SAM.gov search per phrase")
    p.add_argument("--naics", nargs="*", default=[], help="NAICS codes, e.g. 541511 541715")
    p.add_argument("--set-aside", nargs="*", default=[], help="Set-aside codes, e.g. SBA 8A SDVOSBC WOSB")
    p.add_argument("--days", type=int, default=7, help="Posted or updated in the last N days (default 7)")
    p.add_argument("--max", type=int, default=25, help="Maximum solicitations (default 25)")
    p.add_argument("--no-sbir", action="store_true", help="Skip SBIR/STTR sources")
    p.add_argument("--no-attachments", action="store_true", help="Metadata only (faster and cheaper)")
    p.add_argument("--uncleared-only", action="store_true", help="Drop opportunities that require a security clearance")
    p.add_argument("--csv", default="rfps.csv", help="CSV output path (default rfps.csv)")
    p.add_argument("--json", help="Also save the full results as JSON")
    p.add_argument("--max-cost", type=float, default=1.0, help="Stop the run before it costs more than this (USD)")
    return p.parse_args()


def row(item: dict) -> dict:
    signals = item.get("signals") or {}
    constraints = signals.get("submission_constraints") or {}
    contacts = [c.get("email") for c in item.get("points_of_contact") or [] if c.get("email")]
    return {
        "response_deadline": (item.get("response_deadline") or "")[:10],
        "title": item.get("title"),
        "agency": " / ".join(x for x in (item.get("agency"), item.get("sub_agency")) if x),
        "notice_type": item.get("notice_type"),
        "set_aside": item.get("set_aside"),
        "clearance_level": signals.get("clearance_level"),
        "evaluation_type": signals.get("evaluation_type"),
        "page_limits": "; ".join(
            dict.fromkeys(f"{p['pages']} page{'' if p['pages'] == 1 else 's'}" for p in constraints.get("page_limits") or [])
        ),
        "compliance": "; ".join(signals.get("security_and_compliance_frameworks") or []),
        "incumbents": "; ".join(signals.get("incumbent_contractors") or []),
        "contract_numbers": "; ".join(signals.get("referenced_contract_numbers") or []),
        "submit_via": "; ".join(constraints.get("delivery_methods") or []),
        "contacts": "; ".join(contacts or signals.get("extracted_contacts") or []),
        "solicitation_number": item.get("solicitation_number"),
        "url": item.get("url"),
    }


def main() -> int:
    args = parse_args()
    token = os.environ.get("APIFY_TOKEN")
    if not token:
        sys.exit("Set APIFY_TOKEN first. Get one free at https://console.apify.com/settings/integrations")

    run_input = {
        "keywords": args.keywords,
        "naicsCodes": args.naics,
        "setAsideTypes": args.set_aside,
        "postedWithinDays": args.days,
        "maxItems": args.max,
        "includeSbir": not args.no_sbir,
        "parseAttachments": not args.no_attachments,
    }
    client = ApifyClient(token)
    print(f"Running {ACTOR_ID} ...")
    run = client.actor(ACTOR_ID).call(run_input=run_input, max_total_charge_usd=args.max_cost)
    if not run or run.get("status") != "SUCCEEDED":
        sys.exit(f"Run did not finish: {run and run.get('status')}")

    items = list(client.dataset(run["defaultDatasetId"]).iterate_items(clean=True))
    if args.uncleared_only:
        items = [i for i in items if (i.get("signals") or {}).get("clearance_level") not in CLEARED]
    rows = sorted((row(i) for i in items), key=lambda r: (r["response_deadline"] == "", r["response_deadline"]))

    with open(args.csv, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    if args.json:
        with open(args.json, "w", encoding="utf-8") as handle:
            json.dump(items, handle, indent=2)

    print(f"Saved {len(rows)} opportunities to {args.csv}")
    for r in rows[:5]:
        print(f"  {r['response_deadline'] or 'no deadline':>10}  {r['title'][:80]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
