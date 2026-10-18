# SAM.gov RFP Scraper with Attachment Parsing (Python)

Find new federal RFPs on **SAM.gov** and **SBIR/STTR** sources, and get the facts buried in the attachments: **clearance level, LPTA vs. best value, incumbent contract numbers, page limits, formatting rules, CMMC/NIST/FedRAMP requirements and every .gov/.mil contact**.

This repo is a small, free Python client for the [SAM.gov & SBIR Federal RFP + Attachment Deep-Parser](https://apify.com/aimindteams/govcon-rfp-deep-parser) on Apify. The Actor does the searching, downloading and PDF/DOCX parsing in the cloud; this script runs it and saves a CSV you can sort in Excel or Google Sheets.

## Why not just search SAM.gov?

SAM.gov search shows the title, number and dates. Whether you can actually bid is decided in the Statement of Work, the Section L/M instructions and the DD254, and opening those one by one takes hours every week. The Actor reads them for you and returns short evidence quotes so you can check each finding in seconds.

| | SAM.gov search | This tool |
|---|---|---|
| Title, number, dates, agency, NAICS, set-aside | Yes | Yes |
| Reads PDF, DOCX and ZIP attachments | No | Yes |
| Clearance level, DD254, polygraph | No | Yes, with quotes |
| LPTA vs. best value vs. HTRO | No | Yes, with quotes |
| Incumbent contract numbers and contractors | No | Yes |
| Page limits, fonts, margins, submission portal | No | Yes |
| CMMC, NIST 800-171, FedRAMP, ITAR, IL levels | No | Yes |
| SBIR/STTR solicitations | Separate site | Included |

## Quick start (no code)

Open the [Actor on the Apify Store](https://apify.com/aimindteams/govcon-rfp-deep-parser) and press **Start**. The default search returns AI, sensor fusion and autonomy opportunities from the last 7 days. Download the results as CSV, Excel or JSON.

## Quick start (Python)

```bash
git clone https://github.com/aimindteams/sam-gov-rfp-scraper
cd sam-gov-rfp-scraper
pip install -r requirements.txt
export APIFY_TOKEN=your_token   # free account: https://console.apify.com/settings/integrations

# Small-business AI and data work posted this week, sorted by deadline
python find_rfps.py --keywords "machine learning" "computer vision" "data analytics" \
    --naics 541511 541512 541715 --set-aside SBA --days 7 --csv rfps.csv

# Only opportunities that do not require a security clearance
python find_rfps.py --keywords "software development" --uncleared-only

# Fast metadata-only run (no attachment parsing)
python find_rfps.py --keywords "cybersecurity" --no-attachments --max 100
```

On Windows PowerShell use `$env:APIFY_TOKEN="your_token"` instead of `export`.

## What the CSV looks like

Illustrative example (invented values):

| response_deadline | title | agency | clearance_level | evaluation_type | page_limits | compliance |
|---|---|---|---|---|---|---|
| 2026-11-13 | AI-Enabled Multi-Sensor Fusion Analytics Support | DEPT OF DEFENSE / DEPT OF THE ARMY | TS/SCI | Best Value Tradeoff | 25 pages | CMMC Level 2; NIST SP 800-171 |
| 2026-11-20 | Cloud Data Platform Modernization | DEPT OF HOMELAND SECURITY | Public Trust | LPTA - Lowest Price Technically Acceptable | 15 pages; 5 pages | FedRAMP Moderate |

Use `--json results.json` to keep the full records, including evidence quotes, every attachment and the SBIR topic list. The full field reference is on the [Store page](https://apify.com/aimindteams/govcon-rfp-deep-parser).

## Run it every morning

On the Store page you can schedule the Actor daily and turn on **Only return new or updated solicitations**, so each run returns, and charges for, only what is new. Connect Slack, email or Google Sheets under Integrations and your team gets a short list of qualified RFPs each morning.

## Use it from AI agents (MCP)

Add this server URL to Claude, ChatGPT, Cursor or any client that supports remote MCP:

```
https://mcp.apify.com?tools=aimindteams/govcon-rfp-deep-parser
```

## Pricing

Pay per solicitation delivered; there is no monthly fee. Current prices are on the [Pricing tab](https://apify.com/aimindteams/govcon-rfp-deep-parser/pricing). Apify's free plan includes monthly platform credit, which covers a lot of test runs. `--max-cost` (default $1) caps any single run.

## FAQ

**Do I need a SAM.gov API key?** No. You can add a free one in the Actor input for a second discovery source.

**What about controlled (CUI) attachments?** Files that require a SAM.gov login are listed but cannot be downloaded; the notice is still delivered with its description signals.

**Is there a weekly digest?** Yes: [SBIR Signal](https://github.com/aimindteams/sbir-signal) is a free weekly newsletter built on this Actor.

## License

The code in this repo is MIT licensed. The Actor itself is a hosted service on Apify.
