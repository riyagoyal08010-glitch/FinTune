import csv
from collections import Counter, defaultdict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "sec_structured_v1_clean.tsv"
)


# Important financial concepts we want to investigate.
TARGET_TAGS = {
    "RevenueFromContractWithCustomerExcludingAssessedTax",
    "Revenues",
    "ProfitLoss",
    "NetIncomeLoss",
    "OperatingIncomeLoss",
    "Assets",
    "Liabilities",
    "StockholdersEquity",
    "CashAndCashEquivalentsAtCarryingValue",
    "IncomeTaxExpenseBenefit",
    "CostOfGoodsAndServicesSold",
    "EarningsPerShareBasic",
    "EarningsPerShareDiluted",
}


tag_counts = Counter()

# company -> tag -> set of dates
company_tag_dates = defaultdict(lambda: defaultdict(set))

# company -> set of tags
company_tags = defaultdict(set)

row_count = 0


print("Reading clean SEC structured data...")


with open(
    INPUT_FILE,
    "r",
    encoding="utf-8",
    newline=""
) as f:

    reader = csv.DictReader(f, delimiter="\t")

    for row in reader:

        row_count += 1

        tag = row["tag"]
        cik = row["cik"]
        ddate = row["ddate"]

        tag_counts[tag] += 1

        if tag in TARGET_TAGS:
            company_tags[cik].add(tag)
            company_tag_dates[cik][tag].add(ddate)

        if row_count % 500_000 == 0:
            print(f"Processed {row_count:,} rows...")


print("\n" + "=" * 60)
print("SEC DATASET CAPABILITY ANALYSIS")
print("=" * 60)

print(f"Total rows: {row_count:,}")


# ---------------------------------------------------------
# 1. Target tag frequency
# ---------------------------------------------------------

print("\nTarget financial tags:")

for tag in TARGET_TAGS:
    print(f"{tag:65} {tag_counts[tag]:>10,}")


# ---------------------------------------------------------
# 2. Companies containing combinations of key facts
# ---------------------------------------------------------

def companies_with(tags):
    return sum(
        all(tag in company_tags[cik] for tag in tags)
        for cik in company_tags
    )


combinations = {
    "Revenue + Net Income": [
        "RevenueFromContractWithCustomerExcludingAssessedTax",
        "NetIncomeLoss",
    ],

    "Revenue + Operating Income": [
        "RevenueFromContractWithCustomerExcludingAssessedTax",
        "OperatingIncomeLoss",
    ],

    "Revenue + Operating Income + Net Income": [
        "RevenueFromContractWithCustomerExcludingAssessedTax",
        "OperatingIncomeLoss",
        "NetIncomeLoss",
    ],

    "Assets + Liabilities + Equity": [
        "Assets",
        "Liabilities",
        "StockholdersEquity",
    ],

    "Revenue + COGS": [
        "RevenueFromContractWithCustomerExcludingAssessedTax",
        "CostOfGoodsAndServicesSold",
    ],

    "Revenue + EPS": [
        "RevenueFromContractWithCustomerExcludingAssessedTax",
        "EarningsPerShareBasic",
    ],
}


print("\nCompanies containing key fact combinations:")

for name, tags in combinations.items():
    count = companies_with(tags)
    print(f"{name:50} {count:>6,}")


# ---------------------------------------------------------
# 3. Companies with multiple periods
# ---------------------------------------------------------

print("\nCompanies with multiple periods for key tags:")

for tag in TARGET_TAGS:

    companies_multiple_periods = sum(
        len(company_tag_dates[cik][tag]) >= 2
        for cik in company_tags
        if tag in company_tag_dates[cik]
    )

    print(
        f"{tag:65} "
        f"{companies_multiple_periods:>6,}"
    )


# ---------------------------------------------------------
# 4. Top 30 overall tags
# ---------------------------------------------------------

print("\nTop 30 XBRL tags overall:")

for tag, count in tag_counts.most_common(30):
    print(f"{count:>10,}  {tag}")


print("\n" + "=" * 60)
print("ANALYSIS COMPLETE")
print("=" * 60)