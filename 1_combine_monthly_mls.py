"""
Combine monthly CRMLS files into Residential-only listing and sold datasets.

"""

import pandas as pd
from datetime import date
from pathlib import Path

input_path = Path("/Users/lindsey/Desktop/IDX/csv")
sold_output = input_path / "combined_sold_transactions.csv"
listing_output = input_path / "combined_listings.csv"


# monthly files to combine: January 2024 through April 2026.
months = pd.period_range("2024-01", "2026-04", freq="M").strftime("%Y%m").tolist()

# match monthly files
# sold files may be named like CRMLSSold202401.csv or CRMLSSold202401_filled.csv
sold_files = []
listing_files = []

for month in months:
    sold_matches = sorted(input_path.glob(f"CRMLSSold{month}*.csv"))
    listing_matches = sorted(input_path.glob(f"CRMLSListing{month}*.csv"))

    if not sold_matches:
        raise FileNotFoundError(f"No sold file found for {month}")
    if not listing_matches:
        raise FileNotFoundError(f"No listing file found for {month}")

    sold_files.append(sold_matches[0])
    listing_files.append(listing_matches[0])

# read each monthly file
sold_dfs = [pd.read_csv(file, low_memory=False) for file in sold_files]
listing_dfs = [pd.read_csv(file, low_memory=False) for file in listing_files]

# row counts before and after concatenation
sold_rows_before_concat = sum(len(df) for df in sold_dfs)
listing_rows_before_concat = sum(len(df) for df in listing_dfs)

sold = pd.concat(sold_dfs, ignore_index=True)
listings = pd.concat(listing_dfs, ignore_index=True)

print(f"Sold rows before concatenation: {sold_rows_before_concat:,}")
print(f"Sold rows after concatenation: {len(sold):,}")
print(f"Listing rows before concatenation: {listing_rows_before_concat:,}")
print(f"Listing rows after concatenation: {len(listings):,}")

# row counts before and after PropertyType == "Residential" filter
sold_rows_before_filter = len(sold)
listing_rows_before_filter = len(listings)

sold = sold[sold["PropertyType"].astype("string").str.strip().eq("Residential")]
listings = listings[listings["PropertyType"].astype("string").str.strip().eq("Residential")]

print(f"Sold rows before Residential filter: {sold_rows_before_filter:,}")
print(f"Sold rows after Residential filter: {len(sold):,}")
print(f"Listing rows before Residential filter: {listing_rows_before_filter:,}")
print(f"Listing rows after Residential filter: {len(listings):,}")

# save the combined datasets
sold.to_csv(sold_output, index=False)
listings.to_csv(listing_output, index=False)


"""
- Sold rows before concatenation: 615,707 | after concatenation: 615,707
- Listing rows before concatenation: 860,898 | after concatenation: 860,898
- Sold rows before Residential filter: 615,707 | after Residential filter: 414,054
- Listing rows before Residential filter: 860,898 |after Residential filter: 547,162
"""

